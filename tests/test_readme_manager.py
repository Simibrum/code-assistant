from markdown_it.token import Token
from code_management import readme_manager

def test_parse_readme():
    """
    Test the parse_readme function from the readme_manager module.

    The function should return a structured form of the README file.
    """
    readme_path = "./README.md"
    result = readme_manager.parse_readme(readme_path)
    assert isinstance(
        result, Token
    ), "The result should be a Token instance."
    assert len(result) > 0, "The result should not be empty."


def test_get_section():
    """
    Test the get_section function from the readme_manager.py file.
    """
    tokens = [
        Token(type="heading_open", tag="h2", content=""),
        Token(type="inline", content="section1"),
        Token(type="inline", content="content1"),
        Token(type="heading_open", tag="h2", content=""),
        Token(type="inline", content="section2"),
        Token(type="inline", content="content2"),
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
    # Import the function to test.

    # Define a sample Markdown file path.
    sample_file_path = './sample.md'

    # Define expected result. This would usually be known from the file content.
    expected_result = ['Heading 1', 'Heading 2']

    # Call the function with the sample file path.
    result = readme_manager.get_headings_from_md_file(sample_file_path)

    # Assert that the result is as expected.
    assert result == expected_result, f'Expected {expected_result}, but got {result}'
