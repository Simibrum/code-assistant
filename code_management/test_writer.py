"""Code for generating test functions."""
from llm.prompts import build_messages




def generate_test(function_code: str) -> str:
    """
    Generate a test function for a given function.

    Args:
        function_name (str): The name of the function to test.
        function_code (str): The source code of the function to test.

    Returns:
        str: The generated test function.
    """
    # Create a prompt for the LLM.
    prompt = create_test_prompt(function_code)
    messages = build_messages(prompt)
    

    
