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
import tempfile

from markdown_it.token import Token

from code_management import readme_manager


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
