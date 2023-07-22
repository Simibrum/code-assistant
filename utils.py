"""
`utils.py`

This module provides utility functions for the Agent.

It contains the following functions:
- `extract_project_description(readme_path: str) -> str`: Extracts the Project Description section 
from a README file.

This module is part of the Agent project, which uses a Language Learning Model (LLM) to generate 
code, tests, and manage a GitHub repository.
"""

import re

def extract_project_description(readme_path: str = "README.md") -> str:
    """
    Extracts the Project Description section from a README file
    for use as a system prompt.

    Args:
        readme_path (str): The path to the README file.

    Returns:
        str: The text of the Project Description section.
    """
    with open(readme_path, 'r', encoding='utf-8') as file:
        readme = file.read()

    # Use regex to find the Project Description section.
    # This pattern finds the text between "## Project Description" and the next "##" heading.
    pattern = r"## Project Description\n(.*?)(?=\n##|$)"
    match = re.search(pattern, readme, re.DOTALL)

    # If a match is found, return the matched text (without leading/trailing whitespace).
    if match:
        return match.group(1).strip()

    # If no match is found, return an empty string.
    return ""
