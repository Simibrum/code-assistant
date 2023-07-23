"""Common prompt building functions."""
import sys
import os
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
    directory_structure = utils.build_directory_structure(start_directory, gitignore_patterns)
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

def build_messages(prompt, messages = None) -> list[dict]:
    """Build a set of chat messages based around the prompt as the last message."""
    if not messages:
        messages = [
            {"role": "system", "content": generate_system_prompt()},
            {"role": "user", "content": generate_directory_prompt()},
            {"role": "user", "content": generate_requirements_prompt()},
        ]
    messages += [{"role": "user", "content": prompt}]
    return messages

def create_test_prompt(function_code: str, function_file: str) -> str:
    """
    Create a prompt for the LLM to generate a test based on the provided function code.

    Args:
        function_code (str): The source code of the function to test.
        function_file (str): The file containing the function to test.

    Returns:
        str: The generated prompt.
    """
    # Include the function code in the prompt.
    prompt = "I would like you to write a pytest unit test.\n\n"
    prompt = "Here is code for the function to test:\n\n" + function_code + "\n\n"
    prompt += "The function to test is in the file " + function_file + "\n\n"
    prompt += (
        "Import the function in the test file using the"
        " [function_file].[function_name] syntax.\n\n"
    )
    prompt += "Call the test `test_[function_name]`."

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
    prompt += "Only return the docstring. Limit to less than 250 words."

    return prompt
