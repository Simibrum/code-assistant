"""Common prompt building functions."""
import os
import sys

import utils


def generate_system_prompt() -> str:
    """
    Generate a system prompt for the LLM.

    Returns:
        str: The generated prompt.
    """
    prompt = "You are a helpful coding assistant."
    project_description = utils.extract_project_description()
    if project_description:
        prompt += f"\n\n{project_description}\n\n"
    prompt += f"The Python version is {sys.version}\n"
    return prompt


def generate_directory_prompt() -> str:
    """
    Generate a prompt for the LLM with the current directory structure.

    Returns:
        str: The generated prompt.
    """
    # Get the parent directory of the current file directory
    start_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # My .gitignore file is in the parent directory
    gitignore_path = os.path.join(start_directory, ".gitignore")

    gitignore_patterns = utils.read_gitignore(gitignore_path)
    directory_structure = utils.build_directory_structure(
        start_directory, gitignore_patterns
    )
    prompt = f"The directory structure for the project is:\n{directory_structure}"

    return prompt


def generate_requirements_prompt() -> str:
    """
    Generate a prompt for the LLM with the contents fo the requirements.txt file.

    Returns:
        str: The generated prompt.
    """
    requirements_contents = utils.read_requirements_txt()
    prompt = "The installed packages as set out in `requirements.txt` are:\n"
    prompt += requirements_contents
    return prompt


def build_messages(
    prompt, messages=None, add_dir: bool = True, add_requirements: bool = True
) -> list[dict]:
    """Build a set of chat messages based around the prompt as the last message."""
    if not messages:
        messages = [
            {"role": "system", "content": generate_system_prompt()},
        ]
        if add_dir:
            messages.append({"role": "user", "content": generate_directory_prompt()})
        if add_requirements:
            messages.append({"role": "user", "content": generate_requirements_prompt()})
    messages += [{"role": "user", "content": prompt}]
    return messages


def create_test_prompt(
    function_code: str, function_file: str, test_name: str = None
) -> str:
    """
    Create a prompt for the LLM to generate a test based on the provided function code.

    Args:
        function_code (str): The source code of the function to test.
        function_file (str): The file containing the function to test.
        test_name (str, optional): The name of the test. Defaults to None.

    Returns:
        str: The generated prompt.
    """
    # Include the function code in the prompt.
    prompt = "I would like you to write a pytest unit test.\n\n"
    prompt += "Here is code for the function to test:\n\n" + function_code + "\n\n"
    prompt += "The function to test is in the file " + function_file + "\n\n"
    prompt += (
        "Import the function in the test file using the"
        " [function_file].[function_name] syntax.\n\n"
    )
    if test_name:
        prompt += "Call the test: `" + test_name + "`."
    else:
        prompt += "Call the test: `test_[function_name]`."

    return prompt


def revise_test_prompt(
    original_test_code: str, function_code: str, test_output: str
) -> str:
    """Get a prompt for the LLM to revise a test."""
    prompt = "I have an LLM that has generated the test code for the function below."
    prompt += "The test is currently failing with the failure message as below."
    prompt += "Can you revise the test code so that the test passes?"
    prompt += "* Please do not use fixtures at this stage, so that the test code functions independently."
    prompt += "* Please keep the test function name the same."
    prompt += "\n\n"
    prompt += f"Original generated test code: {original_test_code}\n\n"
    prompt += f"Function code: {function_code}\n\n"
    prompt += f"Pytest output: {test_output}\n\n"
    return prompt


def create_function_prompt(task_description: str, function_file: str) -> str:
    """
    Create a prompt for the LLM to generate a function based on the provided task description.

    Args:
        task_description (str): The description of the task for the new function.
        function_file (str): The file containing the function to test.

    Returns:
        str: The generated prompt.
    """

    # Create a prompt for the LLM.
    prompt = f"Please write a Python function to {task_description}."

    prompt += "The function is to be added to the file " + function_file + "\n\n"

    return prompt


def create_module_docstring_prompt(module_code: str) -> str:
    """
    Create a prompt for the LLM to generate a docstring for a Python module.

    Args:
        module_code (str): The source code of the module.

    Returns:
        str: The generated prompt.
    """
    # Include the module code in the prompt.
    prompt = "Here is some code for a module:\n\n" + module_code + "\n\n"

    # Add the message setting the task.
    prompt += "Please write a docstring for the above module. "
    prompt += "Do NOT include the module code in the docstring. "
    prompt += "Do NOT describe individual functions - just the module as a whole. "
    prompt += "Documentation for individual functions will be provided in function docstrings. "
    prompt += "Only return the docstring. "
    prompt += "Limit the total description to less than 250 words. "
    prompt += "Limit lines to a maximum of 90 characters.\n\n"
    prompt += "The docstring should be in the following format:\n\n"
    prompt += '"""\n[docstring]\n"""\n\n'

    return prompt


def create_function_docstring_prompt(function_code: str) -> str:
    """
    Create a prompt for the LLM to generate a docstring for a Python function.

    Args:
        function_code (str): The source code of the function.

    Returns:
        str: The generated prompt.
    """
    # Include the function code in the prompt.
    prompt = "Here is some code for a function:\n\n" + function_code + "\n\n"

    # Add the message setting the task.
    prompt += "Please write a docstring for the above function. "
    prompt += "Do NOT include the function code in the docstring. "
    prompt += "Only return the docstring. "
    prompt += "Limit the total description to less than 500 words. "
    prompt += "Limit lines to a maximum of 90 characters.\n\n"
    prompt += "The docstring should be in the Google docstring format:\n\n"
    prompt += (
        '"""\n[Short, concise function description]\n\n'
        "Args:\n    [param1]: [desc]\n  [param2]:[desc]\n"
        "Returns:\n    [Return value desc]\n\n"
        '"""\n\n'
    )

    return prompt


def create_todo_list_prompt() -> str:
    """
    Create a prompt for the LLM to generate a TODO list.

    Returns:
        str: The generated prompt.
    """
    # Add the message setting the task.
    prompt = "Please write a markdown TODO list for the project. "
    prompt += "Limit to 10 items."
    prompt += "Limit lines to a maximum of 90 characters.\n\n"
    prompt += "The TODO list should be in the following format:\n\n"
    prompt += "##TODO list\n[ ]- Task 1\n[ ]- Task 2\n[ ]- Task 3\n\n"

    return prompt


def create_task_processing_prompt(task_description: str) -> str:
    """
    Create a prompt for the LLM to perform a task processing action.

    Args:
        task_description (str): The description of the task to process.

    Returns:
        str: The generated prompt.
    """
    prompt = "----\n"
    prompt += "We now want to process a task description.\n\n"
    prompt += "We need to determine whether:\n"
    prompt += "1. The task is too complex and needs to be broken down into subtasks.\n"
    prompt += (
        "2. The task is too obscure and we need further information from the user.\n"
    )
    prompt += "3. The task is manageable and we can generate code for it.\n\n"
    prompt += "Here is the task description:\n\n"
    prompt += task_description + "\n\n"
    prompt += "Only use the functions you have been provided with.\n\n"
    return prompt


def create_task_prompt_from_issue(issue) -> str:
    """
    Create a prompt for the LLM to create a task from an issue.

    Args:
        issue (Issue): the issue from GitHub

    Returns:
        str: the prompt
    """
    task_description = (
        f"* Task from Issue #{issue.number}: {issue.title}\n{issue.body}\n----\n"
    )
    return create_task_processing_prompt(task_description)


def create_reduce_module_descriptions_prompt(initial_description: str) -> str:
    """
    Create a prompt for the LLM to reduce module descriptions.

    Args:
        initial_description (str): Initial string with markdown list.

    Returns:
        str: prompt for reduction.
    """
    prompt = "Can you reduce each of the module descriptions "
    prompt += "below to a single sentence?\n\n"
    prompt += initial_description + "\n\n"
    prompt += "Only use the functions you have been provided with.\n\n"
    prompt += "Keep the same format: '- [module_name]: [module_description]'\n\n"
    return prompt


def create_issue_review_prompt(open_issues: list, titles_only: bool = False) -> str:
    """
    Create a prompt for the LLM to review open issues.

    Args:
        open_issues (list[Issue]): the open issues from GitHub

    Returns:
        str: the prompt
    """
    prompt = "Can you select the easiest issue to solve?\n----\n"
    for issue in open_issues:
        if titles_only:
            prompt += f"* Issue #{issue.number}: {issue.title}\n"
        else:
            prompt += f"* Issue #{issue.number}: {issue.title}\n{issue.body}\n----\n"
    prompt += "Only use the functions you have been provided with.\n\n"
    return prompt
