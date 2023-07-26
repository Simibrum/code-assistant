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
    assert isinstance(
        result, list
    ), "The result should be a list instance."
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
    # Generate a fake Markdown file as a temporary file.
    with tempfile.NamedTemporaryFile(suffix=".md") as temp_file:
        temp_file.write(b"# Heading 1\n## Heading 2\n### Heading 3")
        temp_file.seek(0)
        # Get the headings from the file.
        headings = readme_manager.get_headings_from_md_file(temp_file.name)
        # Assert that the headings are as expected.
        assert headings == ["Heading 1", "Heading 2", "Heading 3"]
