"""
This module provides functions for parsing and manipulating Markdown files. It includes functions to parse a README.md file and return its structured form, retrieve the contents of a specific section from the README.md file, extract all headings from a Markdown file, and replace a portion of text in a Markdown document between two headings.

The `parse_readme` function takes the path to a README.md file and returns the structured form of the file using the `MarkdownIt` library.

The `get_section` function retrieves the contents of a specific section from the structured form of the README.md file.

The `get_headings_from_md_file` function extracts all the headings from a Markdown file.

The `replace_section_in_markdown` function replaces a portion of text in a Markdown document between two headings.

These functions provide convenient utilities for working with Markdown files and can be used to extract specific information or modify the contents of Markdown files programmatically.
"""

from typing import List
import os

from markdown_it import MarkdownIt
from mdformat.renderer import MDRenderer

import utils
from github_management.issue_management import GitHubIssues
from code_management import code_reader
import llm.llm_interface as llm


def parse_readme(readme_path):
    """
    Parse the README.md file and return a structured form.

    Args:
        readme_path (str): The path to the README.md file.

    Returns:
        markdown_it.token.Token: The structured form of the README.md file.
    """
    with open(readme_path, "r", encoding="utf-8") as file:
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
        if token.type == "heading_open" and token.tag == "h2":
            in_section = False
        if in_section and token.type == "inline":
            section_contents.append(token.content)
        if token.type == "inline" and token.content == section_name:
            in_section = True
    return "\n".join(section_contents)


def get_headings_from_md_file(file_path: str) -> List[str]:
    """
    Get all the headings from a Markdown file.

    Args:
        file_path (str): The path to the Markdown file.

    Returns:
        List[str]: A list of the headings in the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    markdown = MarkdownIt()
    tokens = markdown.parse(content)
    headings = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
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
        if token.type == "heading_open":
            if (i < (len(tokens) - 1)) and tokens[i+1].content.lower() == heading.lower():
                start_index = i
            elif start_index is not None:
                end_index = i
                break
    if start_index is None or end_index is None:
        return markdown_text
    replaced_tokens = (
        tokens[:start_index + 3] + markdown.parse(new_text) + tokens[end_index:]
    )
    renderer = MDRenderer()
    options = {}
    env = {}
    output_markdown = renderer.render(replaced_tokens, options, env)
    return output_markdown

def update_readme_summary(readme_text: str) -> str:
    """
    Update the Summary section of the readme with the summary of the project.

    Args:
        readme_text (str): The text of the readme.

    Returns:
        str: The modified readme text.
    """
    # Get the summary of the project
    summary = code_reader.get_summary(".")
    # Replace the Summary section in the readme text
    new_readme_text = replace_section_in_markdown(readme_text, "Summary", summary)

    return new_readme_text


def update_readme_todos(readme_text: str) -> str:
    """
    Update the To Do section of the readme with the issues from the GitHub repository.

    Args:
        readme_text (str): The text of the readme.

    Returns:
        str: The modified readme text.
    """
    # Initialize GitHubIssues and MarkdownManager
    github_issues = GitHubIssues(
        token=os.environ['GITHUB_TOKEN'], repo_name='simibrum/code-assistant')

    # Get all issues from the GitHub repository
    issues = github_issues.get_all_issues()

    # Generate the string for the To Do section
    todo_str = (
        "Loaded from repository [Issues]"
        "(https://github.com/Simibrum/code-assistant/issues):\n\n"
    )
    for issue in issues:
        status = 'X' if issue.state == 'closed' else ' '
        todo_str += f"- [{status}] {issue.title}\n"

    # Replace the To Do section in the readme text
    new_readme_text = replace_section_in_markdown(readme_text, "To do", todo_str)

    return new_readme_text

def update_agent_structure(readme_text: str) -> str:
    """
    Update the Agent Structure section of the readme.

    Args:
        readme_text (str): The text of the readme.

    Returns:
        str: The modified readme text.
    """
    section_string = ""
    # Get the directory structure of the repository
    repository_structure = utils.build_directory_structure(".")
    # Add the directory structure to the Agent Structure section
    section_string += f"""\n```\n{repository_structure}\n```\n\n"""
    # Get a one line summary of the repository files based on docstrings
    module_descriptions = code_reader.read_code_file_descriptions(".")
    description_string = "\n".join(
        f"- `{file_path}`: {module_description}"
        for file_path, module_description in module_descriptions.items()
    )
    # Reduce the descriptions using LLM
    reduced_string = llm.reduce_module_descriptions(description_string)
    # Add the reduced descriptions to the Agent Structure section
    section_string += f"""The following files are included in the repository:\n\n{reduced_string}"""

    # Replace the Agent Structure section in the readme text
    new_readme_text = replace_section_in_markdown(
        readme_text, "Agent Structure", section_string)

    return new_readme_text
