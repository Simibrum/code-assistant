'''```python
from unittest import mock
from unittest.mock import patch
import llm.prompts as prompts

def test_generate_system_prompt() -> None:
    """
    Test the function generate_system_prompt from the prompts module.
    """
    with patch(
        'llm.prompts.utils.extract_project_description', 
        return_value='Project Description'
    ):
        result = prompts.generate_system_prompt()
    assert result.startswith('You are a helpful coding assistant.')
    assert 'Project Description' in result
    assert 'Python version is' in result

def test_generate_directory_prompt() -> None:
    """
    Test the generate_directory_prompt function from the prompts module.
    """
    result = prompts.generate_directory_prompt()
    assert isinstance(result, str)
    assert result != ''

def test_generate_requirements_prompt() -> None:
    """
    Test the generate_requirements_prompt function from the prompts module.

    We mock the utils.read_requirements_txt function to return a known string, and assert
    that the generate_requirements_prompt function returns the expected prompt.
    """
    with mock.patch(
        'llm.prompts.utils.read_requirements_txt', 
        return_value='requirements_contents'
    ):
        assert prompts.generate_requirements_prompt() == (
            'The installed packages as set out in `requirements.txt` are:\\nrequirements_contents'
        )

def test_build_messages() -> None:
    """
    Test the build_messages function.
    """
    prompt = 'Test prompt'
    messages = prompts.build_messages(prompt'''
from unittest import mock
from unittest.mock import patch
import llm.prompts as prompts

def test_generate_system_prompt():
    """
    Test the function generate_system_prompt from the prompts module.
    """
    with patch('llm.prompts.utils.extract_project_description', return_value='Project Description'):
        result = prompts.generate_system_prompt()
    assert result.startswith('You are a helpful coding assistant.')
    assert 'Project Description' in result
    assert 'Python version is' in result

def test_generate_directory_prompt():
    """
    Test the generate_directory_prompt function from the prompts module.
    """
    result = prompts.generate_directory_prompt()
    assert isinstance(result, str)
    assert result != ''

def test_generate_requirements_prompt() -> None:
    """
    Test the generate_requirements_prompt function from the prompts module.
    
    We mock the utils.read_requirements_txt function to return a known string, and assert
    that the generate_requirements_prompt function returns the expected prompt.
    """
    with mock.patch('llm.prompts.utils.read_requirements_txt', return_value='requirements_contents'):
        assert prompts.generate_requirements_prompt() == 'The installed packages as set out in `requirements.txt` are:\nrequirements_contents'

def test_build_messages():
    """Test the build_messages function."""
    prompt = 'Test prompt'
    messages = prompts.build_messages(prompt)
    assert isinstance(messages, list)
    assert len(messages) == 4
    assert messages[-1] == {'role': 'user', 'content': prompt}
    for message in messages[:-1]:
        assert message['role'] in ['system', 'user']
        assert isinstance(message['content'], str)

def test_create_function_prompt():
    """
    Test the create_function_prompt function.
    """
    task_description = 'summarise the function'
    function_file = './llm/prompts.py'
    expected_prompt = 'Please write a Python function to summarise the function.The function is to be added to the file ./llm/prompts.py\n\n'
    actual_prompt = prompts.create_function_prompt(task_description, function_file)
    assert actual_prompt == expected_prompt, f'Expected: {expected_prompt}, but got: {actual_prompt}'

def test_create_module_docstring_prompt():
    """
    Test the function create_module_docstring_prompt from the prompts module.
    """
    module_code = "def hello_world():\n    print('Hello, world!')"
    prompt = prompts.create_module_docstring_prompt(module_code)
    expected_prompt = 'Here is some code for a module:\n\n' + module_code + '\n\nPlease write a docstring for the above module.' + ' Only return the docstring. Limit to less than 250 words.'
    assert prompt == expected_prompt

def test_create_test_prompt():
    """
    Test the create_test_prompt function.

    Args:
        None

    Returns:
        None
    """
    function_code = 'def test_function():\n    pass'
    function_file = './llm/prompts.py'
    expected_output = 'I would like you to write a pytest unit test.\n\nHere is code for the function to test:\n\ndef test_function():\n    pass\n\nThe function to test is in the file ./llm/prompts.py\n\nImport the function in the test file using the [function_file].[function_name] syntax.\n\nCall the test `test_[function_name]`.'
    output = prompts.create_test_prompt(function_code, function_file)
    assert output == expected_output, f'Expected: {expected_output}, but got: {output}'