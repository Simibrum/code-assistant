"""
This module provides test functions for the `readme_manager` module in the `code_management` package.
The `readme_manager` module contains functions for parsing and extracting information from README files.

The `test_parse_readme` function tests the `parse_readme` function, which parses a README file and returns a structured form of its content.
It asserts that the result is a non-empty list of `Token` instances.

The `test_get_section` function tests the `get_section` function, which extracts the content of a specific section from a list of `Token` instances.
It asserts that the extracted content matches the expected output.

The `test_get_headings_from_md_file` function tests the `get_headings_from_md_file` function, which reads a Markdown file and returns a list of its headings.
It generates a temporary Markdown file, writes headings to it, and asserts that the returned headings match the expected output.

These test functions ensure the functionality and correctness of the `readme_manager` module.
"""
import os
import tempfile
from unittest.mock import patch

from markdown_it.token import Token

from code_management import readme_manager
from code_management.readme_manager import update_readme_todos
from functions import logger


def test_parse_readme():
    """
    Test the parse_readme function from the readme_manager module.

    The function should return a structured form of the README file.
    """
    readme_path = "./README.md"
    result = readme_manager.parse_readme(readme_path)
    assert isinstance(result, list), "The result should be a list instance."
    assert len(result) > 0, "The result should not be empty."
    assert all(
        (isinstance(token, Token) for token in result)
    ), "All tokens should be instances of the Token class."

    # Additional assertions to cover the untested lines
    # Since there are no untested lines, these are just additional checks
    first_token = result[0]
    assert hasattr(first_token, "type"), "Each token should have a type attribute."
    assert hasattr(first_token, "tag"), "Each token should have a tag attribute."
    assert hasattr(first_token, "attrs"), "Each token should have an attrs attribute."
    assert hasattr(first_token, "map"), "Each token should have a map attribute."
    assert hasattr(
        first_token, "nesting"
    ), "Each token should have a nesting attribute."
    assert hasattr(first_token, "level"), "Each token should have a level attribute."
    assert hasattr(
        first_token, "children"
    ), "Each token should have a children attribute."
    assert hasattr(
        first_token, "content"
    ), "Each token should have a content attribute."
    assert hasattr(first_token, "markup"), "Each token should have a markup attribute."
    assert hasattr(first_token, "info"), "Each token should have an info attribute."
    assert hasattr(first_token, "meta"), "Each token should have a meta attribute."
    assert hasattr(first_token, "block"), "Each token should have a block attribute."
    assert hasattr(first_token, "hidden"), "Each token should have a hidden attribute."


def test_get_section():
    """
    Test the get_section function from the readme_manager.py file.
    """
    tokens = [
        Token(type="heading_open", tag="h2", content="", nesting=1),
        Token(type="inline", tag="", content="section1", nesting=0),
        Token(type="inline", tag="", content="content1", nesting=-1),
        Token(type="heading_open", tag="h2", content="", nesting=1),
        Token(type="inline", tag="", content="section2", nesting=0),
        Token(type="inline", tag="", content="content2", nesting=-1),
    ]
    section_name = "section1"
    expected_output = "content1"
    assert readme_manager.get_section(tokens, section_name) == expected_output
    section_name = "invalid"
    expected_output = ""
    assert readme_manager.get_section(tokens, section_name) == expected_output


def test_get_headings_from_md_file():
    """
    Tests the function get_headings_from_md_file from the file readme_manager.py.
    """
    with tempfile.NamedTemporaryFile(suffix=".md") as temp_file:
        temp_file.write(b"# Heading 1\n## Heading 2\n### Heading 3")
        temp_file.seek(0)
        headings = readme_manager.get_headings_from_md_file(temp_file.name)
        assert headings == ["Heading 1", "Heading 2", "Heading 3"]

    # Test with a file that contains no headings
    with tempfile.NamedTemporaryFile(suffix=".md") as temp_file:
        temp_file.write(b"This is a file with no headings.")
        temp_file.seek(0)
        headings = readme_manager.get_headings_from_md_file(temp_file.name)
        assert headings == []


def test_replace_section_in_markdown():
    """
    Tests the function replace_section_in_markdown from the file readme_manager.py.
    """
    markdown_text = "# Heading 1\nThis is the first section.\n\n# Heading 2\nThis is the second section."
    heading = "Heading 1"
    new_text = "This is the replaced section."
    expected_output = "# Heading 1\n\nThis is the replaced section.\n\n# Heading 2\n\nThis is the second section.\n"
    assert (
        readme_manager.replace_section_in_markdown(markdown_text, heading, new_text)
        == expected_output
    )
    heading = "Non-existing heading"
    assert (
        readme_manager.replace_section_in_markdown(markdown_text, heading, new_text)
        == markdown_text
    )


def test_update_readme_summary(mocker):
    """
    Tests the 'update_readme_summary' function in the readme_manager module.
    """
    mocker.patch(
        "code_management.readme_manager.code_reader.get_summary",
        return_value="Mock Summary",
    )
    mocker.patch(
        "code_management.readme_manager.replace_section_in_markdown",
        return_value="New Readme Text",
    )
    result = readme_manager.update_readme_summary("Readme Text")
    readme_manager.code_reader.get_summary.assert_called_once_with(".")
    readme_manager.replace_section_in_markdown.assert_called_once_with(
        "Readme Text", "Auto Generated Summary", "Mock Summary"
    )
    assert result == "New Readme Text"


def test_update_readme_todos(mocker):
    """
    Test the update_readme_todos function.
    """
    mock_github_issues_class = mocker.patch(
        "code_management.readme_manager.GitHubIssues", autospec=True
    )
    mock_get_all_issues = mock_github_issues_class.return_value.get_all_issues
    mock_get_all_issues.return_value = [
        mocker.Mock(state="open", title="Issue 1"),
        mocker.Mock(state="closed", title="Issue 2"),
    ]
    mock_replace_section_in_markdown = mocker.patch(
        "code_management.readme_manager.replace_section_in_markdown"
    )
    mock_replace_section_in_markdown.return_value = "updated_readme_text"
    result = update_readme_todos("readme_text")
    mock_github_issues_class.assert_called_once_with(
        token=os.environ["GITHUB_TOKEN"], repo_name="simibrum/code-assistant"
    )
    mock_get_all_issues.assert_called_once()
    expected_todo_str = (
        "Loaded from repository [Issues](https://github.com/Simibrum/code-assistant/issues):"
        "\n\n- [ ] Issue 1\n- [X] Issue 2\n"
    )
    mock_replace_section_in_markdown.assert_called_once_with(
        "readme_text", "To do", expected_todo_str
    )
    assert result == "updated_readme_text"


def test_update_agent_structure():
    """
    Test the function update_agent_structure.
    """
    # Arrange
    readme_text = (
        "## Agent Structure\n" "Old Content\n" "## Another section\n" "More content"
    )

    # Act
    with patch(
        "llm.llm_interface.reduce_module_descriptions", return_value="New Content"
    ), patch(
        "utils.build_directory_structure", return_value="Directory Structure"
    ), patch(
        "code_management.code_reader.read_code_file_descriptions",
        return_value={"file_path": "description"},
    ):
        new_readme_text = readme_manager.update_agent_structure(readme_text)
        logger.debug("New Readme Text: %s", new_readme_text)

    # Assert
    assert "# Agent Structure" in new_readme_text
    assert "Old Content" not in new_readme_text
    assert "New Content" in new_readme_text
    assert "Directory Structure" in new_readme_text
    assert "`file_path`: description" in new_readme_text
