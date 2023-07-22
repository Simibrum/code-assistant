"""Code for generating test functions."""
from utils import extract_project_description


def create_test_prompt(function_code: str) -> str:
    """
    Create a prompt for the LLM to generate a test based on the provided function code.

    Args:
        function_code (str): The source code of the function to test.

    Returns:
        str: The generated prompt.
    """
    # Start the prompt with a system message setting the task.
    prompt = "You are a helpful coding assistant."
    project_description = extract_project_description()
    if project_description:
        prompt += f"\n\n{project_description}\n\n"

    # Include the function code in the prompt.
    prompt += "Here is some code for a function:\n\n" + function_code + "\n\n"

    # Add the message setting the task.
    prompt += "Please write a pytest unit test for the above function."
    prompt += "Only return the code. Use comments in the code to describe functionality."

    return prompt
