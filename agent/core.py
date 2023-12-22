"""
This is the main script that uses all the other components to perform tasks. 
It would contain the main loop of the agent, where it determines the next task, 
performs the task, evaluates the result, and repeats.
"""
import ast
import os

import black

import llm.llm_interface as llm
import utils
from code_management import readme_manager
from code_management.code_database import (
    setup_db,
    CodeFunction,
    add_test_to_db,
    link_tests,
    compute_test_name,
)
from code_management.code_reader import create_code_objects
from functions import logger
from git_management.git_handler import GitHandler
from github_management.issue_management import GitHubIssues
from llm.task_management import process_task


def generate_tests():
    """
    Generate tests for the functions in the codebase.
    """
    # Get the paths of all the python files in the present directory.
    python_files = utils.get_python_files()

    # Iterate through the files
    for python_file in python_files:
        # Extract the functions from the file.
        functions = utils.extract_functions_from_file(python_file)

        # Write the test to a file.
        test_file_name = f"tests/test_{python_file.split('/')[-1]}"

        # If the test file exists, extract the function names from it.
        existing_test_functions = set()
        if os.path.exists(test_file_name):
            logger.info("Test file %s already exists.", test_file_name)
            existing_test_functions = set(
                name for name, _ in utils.extract_functions_from_file(test_file_name)
            )
            logger.info(
                "Found %s existing test functions.", len(existing_test_functions)
            )
            logger.debug("Existing test functions: %s", existing_test_functions)

        # Iterate through the functions.
        for function_name, function_code in functions:
            # Only generate and write the test if it doesn't already exist.
            if f"test_{function_name}" not in existing_test_functions:
                # Generate a test for the function.
                logger.info("Generating test for function %s", function_name)
                test_code, imports = llm.generate_test(
                    function_code, function_file=python_file
                )
                if test_code is None:
                    logger.info(
                        "Failed to generate test for function %s", function_name
                    )
                    continue
                logger.debug("Test code: %s", test_code)
                logger.info("Writing imports to file: %s", imports)
                utils.add_imports(test_file_name, imports)
                logger.info("Writing test to file %s", test_file_name)
                with open(test_file_name, "a", encoding="utf-8") as file:
                    file.write("\n\n" + test_code + "\n\n")


def generate_module_docstrings():
    """
    Generate module docstrings for all Python files that don't have one.
    """
    # Get the Python files in the directory.
    python_files = utils.get_python_files(skip_tests=False)

    # Process each file.
    for file_path in python_files:
        # Parse the existing code.
        with open(file_path, "r", encoding="utf-8") as file:
            module = ast.parse(file.read())

        # Check if the module has a docstring.
        if ast.get_docstring(module) is not None:
            logger.info("Module %s already has a docstring.", file_path)
            continue  # Skip this file if it has a docstring.

        logger.info("Generating docstring for module %s", file_path)
        # Generate a docstring for the module.
        with open(file_path, "r", encoding="utf-8") as file:
            file_contents = file.read()
        # Skip if the file is empty.
        if not file_contents:
            continue
        docstring = llm.generate_module_docstring(file_contents)
        logger.debug("Generated docstring: %s", docstring)

        # Add the docstring to the module.
        docstring_node = ast.Expr(value=ast.Str(s=docstring))
        module.body.insert(0, docstring_node)

        # Unparse the modified AST back to code.
        new_code = ast.unparse(module)
        logger.debug("New code: %s", new_code)
        # Format code with black
        fmt_code = utils.format_code(new_code)
        logger.debug("Formatted code: %s", fmt_code)
        logger.info("Writing docstring to file %s", file_path)
        # Write the modified code back to the file.
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(fmt_code)


def format_modules():
    """
    Format all Python files in the current directory.
    """
    # Get the Python files in the directory.
    python_files = utils.get_python_files(skip_tests=False)

    # Process each file.
    for file_path in python_files:
        # Parse the existing code.
        logger.info("Formatting module %s", file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            original_code = file.read()
        try:
            # Format code with black
            fmt_code = utils.format_code(original_code)
            logger.debug("Formatted code: %s", fmt_code)
            logger.info("Writing formatted code to file %s", file_path)
            # Write the modified code back to the file.
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(fmt_code)
        except black.NothingChanged:
            logger.info("No changes to file %s", file_path)


def get_task_description():
    """Get a task description from the user."""
    print("Enter task description:")
    task_description = input()
    logger.debug("Task description: %s", task_description)
    return task_description


def generate_function_for_task(task_description: str, function_file: str):
    """Generate a python function to perform a task.

    Args:
        task_description (str): Description of task to allow LLM to
        generate function code in Python.
        function_file (str): Path to file where function will be written.
    """
    # Generate code using the LLM.
    function_code, imports = llm.generate_code(
        task_description, function_file=function_file
    )

    if not function_code:
        print("No code generated.")
        return
    logger.debug("Function code: %s", function_code)

    if imports:
        logger.info("Writing imports to file: %s", imports)
        utils.add_imports(function_file, imports)

    # Append the generated code to the end of the file.
    with open(function_file, "a", encoding="utf-8") as file:
        file.write("\n" + function_code + "\n")


def get_further_information(questions_for_user: list):
    """Get further information about a task from a user using chat.

    Args:
        questions_for_user (list): List of strings containing
        questions to consecutively ask the user to get further information.
    """
    # Ask user questions to get further information.
    extra_info_string = ""
    for question in questions_for_user:
        print(question)
        user_response = input()
        extra_info_string += f"{question}\n{user_response}\n"
        logger.debug("User response: %s", user_response)
    return extra_info_string


def run_task(task_description: str = None, depth: int = 0, max_depth: int = 3):
    """Main function."""
    if not task_description:
        task_description = get_task_description()

    if depth >= max_depth:
        raise ValueError(f"Maximum recursion depth ({max_depth}) exceeded")

    function, parameters = process_task(task_description)
    logger.debug("Function: %s", function)
    logger.debug("Parameters: %s", parameters)

    # Base case: If there are no parameters this is a standard string response
    if not parameters:
        print(function)
        return

    # Recursive cases:
    if function == "generate_function_for_task":
        generate_function_for_task(**parameters)
    elif function == "get_further_information_from_user":
        extra_info_string = get_further_information(**parameters)
        # Resubmit the task description with the extra information.
        task_description = task_description + "\n" + extra_info_string
        run_task(task_description, depth=depth + 1)
    elif function == "divide_and_process_sub_tasks":
        for subtask in parameters:
            run_task(subtask, depth=depth + 1)


def run_task_from_next_issue():
    """Run a task based on the next easiest issue."""
    logger.info("Running task from next issue.")
    gh_issues = GitHubIssues()
    # Get the next issue.
    issue = gh_issues.get_next_issue()
    if not issue:
        logger.info("No issues to process.")
        return
    # Generate task description from the issue
    task_description = gh_issues.task_from_issue(issue)
    logger.debug("Task description: %s", task_description)
    # Create a new branch for the issue
    logger.info("Creating new branch for issue %s", issue.number)
    branch_name = gh_issues.generate_branch_name(issue)
    # Switch to the new branch
    git_handler = GitHandler()
    git_handler.create_new_branch(branch_name)
    # Run the task.
    logger.info("Running task.")
    run_task(task_description)
    # Create tests
    logger.info("Generating tests.")
    generate_tests()


def update_readme():
    """Update multiple sections of the readme."""
    # Read the readme
    with open("README.md", "r", encoding="utf-8") as readme_file:
        readme_text = readme_file.read()

    # Update the Project Summary section
    new_readme_text = readme_manager.update_readme_summary(readme_text)
    # Update the Agent Structure section
    new_readme_text = readme_manager.update_agent_structure(new_readme_text)
    # Update the To Do section
    new_readme_text = readme_manager.update_readme_todos(new_readme_text)

    # Write the new readme text to the file
    with open("README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(new_readme_text)


def update_todos():
    """Update the To Do section of the readme."""
    # Read the readme
    with open("README.md", "r", encoding="utf-8") as readme_file:
        readme_text = readme_file.read()

    # Update the To Do section
    new_readme_text = readme_manager.update_readme_todos(readme_text)

    # Write the new readme text to the file
    with open("README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(new_readme_text)


def populate_db(start_dir: str = "."):
    """Populate the database with the code in the project.

    Args:
        start_dir (str): The path to the directory to read.
    """
    db_session = setup_db()
    for file_path in utils.get_python_files(start_dir, skip_tests=False):
        create_code_objects(db_session, file_path)
    db_session.commit()
    link_tests(db_session)
    db_session.close()


def generate_test_from_function(function: CodeFunction, test_name: str):
    logger.info("Generating test for function %s", function.function_name)
    test_code, imports = llm.generate_test(
        function.function_string, function_file=function.file_path, test_name=test_name
    )
    if test_code is None:
        logger.info("Failed to generate test for function %s", function.function_name)
        return None
    return test_code, imports


def write_test_to_file(function, test_code, imports):
    test_file_name = f"tests/test_{function.file_path.split('/')[-1]}"
    logger.debug("Test code: %s", test_code)
    logger.info("Writing imports to file: %s", imports)
    try:
        utils.add_imports(test_file_name, imports)
    except SyntaxError:
        logger.info("Failed to add imports to file %s", test_file_name)
        return None

    logger.info("Writing test to file %s", function.file_path)
    with open(test_file_name, "a", encoding="utf-8") as file:
        file.write("\n\n" + test_code + "\n\n")
    return test_file_name


def generate_tests_from_db():
    """Generate tests for all functions in the database."""
    # Get all the functions from the database.
    db_session = setup_db()
    functions = db_session.query(CodeFunction).all()
    # Iterate through the functions.
    for function in functions:
        # Check for existing tests.
        if function.tests:
            logger.info("Function %s already has a test.", function.function_name)
            continue
        # Generate a test name
        test_name = compute_test_name(db_session, function)
        # Generate a test for the function.
        outputs = generate_test_from_function(function, test_name)
        if outputs is None:
            continue
        test_code, imports = outputs
        # Write tests to file
        test_file_name = write_test_to_file(function, test_code, imports)
        if test_file_name is None:
            continue
        # Add the test to the database
        add_test_to_db(db_session, function, test_code, test_file_name)
    db_session.commit()
    db_session.close()
