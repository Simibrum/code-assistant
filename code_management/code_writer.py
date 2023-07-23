"""
This script would handle writing code to your Python files, 
including adding new functions or refactoring existing ones.
"""
from llm.llm_interface import generate_code

def add_function_to_file(file_path: str, task_description: str):
    """
    Generate a new function based on a task description and add it to a Python file.

    Args:
        file_path (str): The path to the Python file.
        task_description (str): The description of the task for the new function.
    """
    # Create a prompt for the LLM.
    prompt = f"Please write a Python function to {task_description}."

    # Generate code using the LLM.
    function_code = generate_code(prompt, function_file=file_path)

    if not function_code:
        print("No code generated.")
        return

    # Append the generated code to the end of the file.
    with open(file_path, 'a', encoding="utf-8") as file:
        file.write("\n" + function_code + "\n")
