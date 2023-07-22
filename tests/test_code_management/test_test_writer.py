"""Test the test writer."""
from code_management.test_writer import create_test_prompt


def test_create_test_prompt():
    """Test that create_test_prompt returns the correct prompt."""
    # Define a simple function code and a path to a README file.
    function_code = """
def add(a, b):
    return a + b
"""
    # Call create_test_prompt with the function code and README path.
    prompt = create_test_prompt(function_code)

    # Check that the prompt includes the function code.
    assert function_code.strip() in prompt

    # Check that the prompt includes the correct user message.
    assert "Please write a pytest unit test for the above function." in prompt
