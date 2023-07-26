from typing import List
from markdown_it import MarkdownIt

def parse_readme(readme_path):
    """
    Parse the README.md file and return a structured form.

    Args:
        readme_path (str): The path to the README.md file.

    Returns:
        markdown_it.token.Token: The structured form of the README.md file.
    """
    with open(readme_path, 'r', encoding="utf-8") as file:
        contents = file.read()

    markdown = MarkdownIt()
    tokens = markdown.parse(contents)

    return tokens

def get_section(tokens, section_name):
    """
    Get the contents of a specific section from the structured form of the README.md file.

    Args:
        tokens (list[markdown_it.token.Token]): The structured form of the README.md file.
        section_name (str): The name of the section to retrieve.

    Returns:
        str: The contents of the section.
    """
    in_section = False
    section_contents = []

    for token in tokens:
        if token.type == 'heading_open' and token.tag == 'h2':
            in_section = False

        if in_section and token.type == 'inline':
            section_contents.append(token.content)

        if token.type == 'inline' and token.content == section_name:
            in_section = True

    return '\n'.join(section_contents)


def get_headings_from_md_file(file_path: str) -> List[str]:
    """
    Get all the headings from a Markdown file.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        List[str]: A list of the headings in the file.
    """
    # Read the file content.
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Parse the content.
    markdown = MarkdownIt()
    tokens = markdown.parse(content)

    # Extract the headings.
    headings = []

    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            # The next token should be an 'inline' token containing the heading text.
            if i < len(tokens) - 1:
                next_token = tokens[i + 1]
                headings.append(next_token.content)

    return headings

def replace_section_in_markdown(markdown_text: str, heading: str, new_text: str) -> str:
    """
    Replaces a portion of text in a Markdown document between two headings.

    Args:
        markdown_text (str): The Markdown text.
        heading (str): The name of the first heading.
        new_text (str): The new text to replace the existing content between the first heading and the next heading.

    Returns:
        str: The modified Markdown text.
    """
    markdown = MarkdownIt()
    tokens = markdown.parse(markdown_text)
    start_index = None
    end_index = None
    for i, token in enumerate(tokens):
        if token.type == 'heading_open' and token.content.lower() == heading.lower():
            start_index = i
        elif start_index is not None and token.type == 'heading_open':
            end_index = i
            break
    if start_index is None or end_index is None:
        return markdown_text
    replaced_tokens = tokens[:start_index+1] + markdown.parse(new_text) + tokens[end_index:]
    return ''.join(token.content for token in replaced_tokens)
