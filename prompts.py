import sys

from functions import read_gitignore, build_directory_structure, read_requirements_txt


SYSTEM_PROMPT = f"""
    You are a coding assistant. You are building a Python application. 
    The Python version is {sys.version}
    
    The current directory structure and installed packages are set out in subsequent messages.
    
    You task is to help write clear and concise code.
    Please use docstrings and properly document code.
    The code should be modular and follow a test-driven development approach. 
    I will prompt you to write a function and then prompt you to write the tests.
    I will feedback any errors in testing."
"""

def get_directory_prompt(start_path: str, git_ignore_path: str) -> str:
    """Get a prompt that sets out the directory structure."""
    gitignore_patterns = read_gitignore(gitignore_path)
    directory_structure = build_directory_structure(start_directory, gitignore_patterns, indent=" - ")
    DIRECTORY_PROMPT = f"The directory structure for the project is:\n{directory_structure}"
    return DIRECTORY_PROMPT

def get_installed_packages_prompt(requirements_path: str) -> str:
    """Get a prompt that indicates the installed packages."""
    requirements_txt_contents = read_requirements_txt(requirements_path)
    return f"The installed packages as set out in `requirements.txt` are:\n{requirements_txt_contents}"