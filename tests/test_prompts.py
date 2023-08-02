"""
Tests for the prompts.
"""
from unittest import mock
from unittest.mock import MagicMock, patch

import llm.prompts as prompts


def test_generate_system_prompt():
    """
    Test the function generate_system_prompt from the prompts module.
    """
    with patch(
        "llm.prompts.utils.extract_project_description",
        return_value="Project Description",
    ):
        result = prompts.generate_system_prompt()
    assert result.startswith("You are a helpful coding assistant.")
    assert "Project Description" in result
    assert "Python version is" in result


def test_generate_directory_prompt():
    """
    Test the generate_directory_prompt function from the prompts module.
    """
    result = prompts.generate_directory_prompt()
    assert isinstance(result, str)
    assert result != ""


def test_generate_requirements_prompt() -> None:
    """
    Test the generate_requirements_prompt function from the prompts module.

    We mock the utils.read_requirements_txt function to return a known string, and assert
    that the generate_requirements_prompt function returns the expected prompt.
    """
    with mock.patch(
        "llm.prompts.utils.read_requirements_txt", return_value="requirements_contents"
    ):
        assert (
            prompts.generate_requirements_prompt()
            == "The installed packages as set out in `requirements.txt` are:\nrequirements_contents"
        )


def test_build_messages():
    """Test the build_messages function."""
    prompt = "Test prompt"
    messages = prompts.build_messages(prompt)
    assert isinstance(messages, list)
    assert len(messages) == 4
    assert messages[-1] == {"role": "user", "content": prompt}
    for message in messages[:-1]:
        assert message["role"] in ["system", "user"]
        assert isinstance(message["content"], str)


def test_create_function_prompt():
    """
    Test the create_function_prompt function.
    """
    task_description = "summarise the function"
    function_file = "./llm/prompts.py"
    expected_prompt = "Please write a Python function to summarise the function.The function is to be added to the file ./llm/prompts.py\n\n"
    actual_prompt = prompts.create_function_prompt(task_description, function_file)
    assert (
        actual_prompt == expected_prompt
    ), f"Expected: {expected_prompt}, but got: {actual_prompt}"


def test_create_module_docstring_prompt():
    """
    Test the function create_module_docstring_prompt from the prompts module.
    """
    module_code = "def hello_world():\n    print('Hello, world!')"
    prompt = prompts.create_module_docstring_prompt(module_code)
    expected_prompt = (
        "Here is some code for a module:\n\n"
        + module_code
        + "\n\nPlease write a docstring for the above module. "
        + "Do NOT include the module code in the docstring. "
        + "Do NOT describe individual functions - just the module as a whole. "
        + "Documentation for individual functions will be provided in function docstrings. "
        + "Only return the docstring. "
        + "Limit the total description to less than 250 words. "
        + "Limit lines to a maximum of 90 characters.\n\n"
        + 'The docstring should be in the following format:\n\n"""\n[docstring]\n"""\n\n'
    )
    assert prompt == expected_prompt


def test_create_test_prompt():
    """
    Test the create_test_prompt function.

    Args:
        None

    Returns:
        None
    """
    function_code = "def test_function():\n    pass"
    function_file = "./llm/prompts.py"
    expected_output = "I would like you to write a pytest unit test.\n\nHere is code for the function to test:\n\ndef test_function():\n    pass\n\nThe function to test is in the file ./llm/prompts.py\n\nImport the function in the test file using the [function_file].[function_name] syntax.\n\nCall the test `test_[function_name]`."
    output = prompts.create_test_prompt(function_code, function_file)
    assert output == expected_output, f"Expected: {expected_output}, but got: {output}"


def test_create_function_docstring_prompt():
    """
    Test the create_function_docstring_prompt function.
    """
    function_code = "def add_numbers(a: int, b: int) -> int:\n    return a + b"
    expected_prompt = "Here is some code for a function:\n\n" + function_code + "\n\n"
    expected_prompt += "Please write a docstring for the above function. "
    expected_prompt += "Do NOT include the function code in the docstring. "
    expected_prompt += "Only return the docstring. "
    expected_prompt += "Limit the total description to less than 500 words. "
    expected_prompt += "Limit lines to a maximum of 90 characters.\n\n"
    expected_prompt += "The docstring should be in the Google docstring format:\n\n"
    expected_prompt += '"""\n[Short, concise function description]\n\n'
    expected_prompt += "Args:\n    [param1]: [desc]\n  [param2]:[desc]\n"
    expected_prompt += "Returns:\n    [Return value desc]\n\n"
    expected_prompt += '"""\n\n'
    actual_prompt = prompts.create_function_docstring_prompt(function_code)
    assert actual_prompt == expected_prompt


def test_create_todo_list_prompt():
    """
    Test the correct generation of a TODO list prompt.
    """
    expected_prompt = "Please write a markdown TODO list for the project. "
    expected_prompt += "Limit to 10 items."
    expected_prompt += "Limit lines to a maximum of 90 characters.\n\n"
    expected_prompt += "The TODO list should be in the following format:\n\n"
    expected_prompt += "##TODO list\n[ ]- Task 1\n[ ]- Task 2\n[ ]- Task 3\n\n"
    assert prompts.create_todo_list_prompt() == expected_prompt


def test_create_task_processing_prompt():
    """
    Test if the create_task_processing_prompt function returns the expected prompt.
    """
    task_description = "The aim is to build an agent that can code itself using an LLM."
    expected_prompt = "----\nWe now want to process a task description.\n\nWe need to determine whether:\n1. The task is too complex and needs to be broken down into subtasks.\n2. The task is too obscure and we need further information from the user.\n3. The task is manageable and we can generate code for it.\n\nHere is the task description:\n\nThe aim is to build an agent that can code itself using an LLM.\n\nOnly use the functions you have been provided with.\n\n"
    assert prompts.create_task_processing_prompt(task_description) == expected_prompt


def test_create_task_prompt_from_issue(mocker):
    """
    Test the 'create_task_prompt_from_issue' function.
    """
    mock_issue = mocker.Mock(number=123, title="Test Issue", body="This is a test issue.")
    mock_create_task_processing_prompt = mocker.patch(
        "llm.prompts.create_task_processing_prompt"
    )

    prompts.create_task_prompt_from_issue(mock_issue)
    expected_task_description = (
        "* Task from Issue #123: Test Issue\nThis is a test issue.\n----\n"
    )
    mock_create_task_processing_prompt.assert_called_once_with(expected_task_description)


def test_create_reduce_module_descriptions_prompt():
    """
    Test the create_reduce_module_descriptions_prompt function from the prompts module.
    """
    initial_description = "- module1: This is a test module."
    result = prompts.create_reduce_module_descriptions_prompt(initial_description)
    expected_output = "Can you reduce each of the module descriptions below to a single sentence?\n\n- module1: This is a test module.\n\nOnly use the functions you have been provided with.\n\nKeep the same format: '- [module_name]: [module_description]'\n\n"
    assert result == expected_output


def test_create_issue_review_prompt():
    """
    Tests the function create_issue_review_prompt.
    """
    # Mocking an issue
    issue1 = MagicMock()
    issue1.number = 1
    issue1.title = 'Test Issue 1'
    issue1.body = 'Test Body 1'
    issue2 = MagicMock()
    issue2.number = 2
    issue2.title = 'Test Issue 2'
    issue2.body = 'Test Body 2'

    issues = [issue1, issue2]

    # Testing with titles_only = False
    result = prompts.create_issue_review_prompt(issues)
    expected = 'Can you select the easiest issue to solve?\n----\n* Issue #1: Test Issue 1\nTest Body 1\n----\n* Issue #2: Test Issue 2\nTest Body 2\n----\nOnly use the functions you have been provided with.\n\n'
    assert result == expected

    # Testing with titles_only = True
    result = prompts.create_issue_review_prompt(issues, titles_only=True)
    expected = 'Can you select the easiest issue to solve?\n----\n* Issue #1: Test Issue 1\n* Issue #2: Test Issue 2\nOnly use the functions you have been provided with.\n\n'
    assert result == expected
