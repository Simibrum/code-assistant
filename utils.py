"""
`utils.py`

This module provides utility functions for the Agent.

It contains the following functions:
- `extract_project_description(readme_path: str) -> str`: Extracts the Project Description section 
from a README file.

This module is part of the Agent project, which uses a Language Learning Model (LLM) to generate 
code, tests, and manage a GitHub repository.
"""
import ast
import os
import re

import black
import isort
from markdown_it import MarkdownIt
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from functions import logger


def extract_project_description(readme_path: str = "README.md") -> str:
    """
    Extracts the Project Description section from a README file
    for use as a system prompt.

    Args:
        readme_path (str): The path to the README file.

    Returns:
        str: The text of the Project Description section.
    """
    if not os.path.exists(readme_path):
        return ""
    with open(readme_path, "r", encoding="utf-8") as file:
        readme = file.read()
    pattern = "## Project Description\\n(.*?)(?=\\n##|$)"
    match = re.search(pattern, readme, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def read_requirements_txt(file_path: str = "requirements.txt") -> str:
    """
    Read the contents of a requirements.txt file.

    Args:
        file_path (str): The path to the requirements.txt file.

    Returns:
        str: The contents of the requirements.txt file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read()
    return contents


def read_gitignore(gitignore_path):
    """
    Read the contents of a .gitignore file.

    Args:
        gitignore_path (str): The path to the .gitignore file.

    Returns:
        list[str]: The contents of the .gitignore file.
    """
    with open(gitignore_path, "r", encoding="utf-8") as file:
        gitignore_patterns = file.readlines()
    return [pattern.strip() for pattern in gitignore_patterns if pattern.strip()]


def should_use_file(file_path: str, ignore_patterns=None):
    """
    Check if a file should be used based on its path and a list of ignore patterns.

    Args:
        file_path (str): The path to the file.
        ignore_patterns (list[str], optional): A list of patterns to ignore. Defaults to None.

    Returns:
        bool: True if the file should be used, False otherwise.
    """
    if not ignore_patterns:
        ignore_patterns = read_gitignore(".gitignore")
    pathspec = PathSpec.from_lines(GitWildMatchPattern, ignore_patterns)
    if pathspec.match_file(file_path):
        return False
    if os.path.basename(file_path) in [".git", ".github", "__pycache__", ".pytest_cache"]:
        return False
    return True


def build_directory_structure(
    start_path: str,
    gitignore_patterns: list[str] = None,
    level: int = 0,
    max_levels: int = None,
    indent: str = "  ",
):
    """
    Build a string representation of the directory structure starting at a given path.

    Args:
        start_path (str): The path to the directory to start from.
        level (int, optional): The current level of the directory structure. Default is 0.
        max_levels (int, optional): The maximum number of levels to include. Default is None.
        indent (str, optional): The string to use for indentation. Default is two spaces.

    Returns:
        str: The string representation of the directory structure.
    """
    if not gitignore_patterns:
        gitignore_patterns = read_gitignore(".gitignore")
    if max_levels is not None and level > max_levels:
        return ""
    structure = ""
    for entry in os.listdir(start_path):
        path = os.path.join(start_path, entry)
        if should_use_file(path, gitignore_patterns):
            structure += indent * level + entry + "\n"
            if os.path.isdir(path):
                structure += build_directory_structure(
                    path, gitignore_patterns, level + 1, max_levels, indent
                )
    return structure


def extract_functions_from_file(file_path: str):
    """
    Extract the names and source code of all functions in a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list[tuple]: A list of tuples, where each tuple contains the function name and source code.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()
    module = ast.parse(source_code)
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    function_data = []
    for function in functions:
        function_code = ast.get_source_segment(source_code, function)
        function_data.append((function.name, function_code))
    return function_data


def add_imports(file_path: str, new_imports: list[str]):
    """
    Add import statements to a Python file, avoiding duplicates.

    Args:
        file_path (str): The path to the Python file.
        new_imports (list[str]): The new import statements to add.
    """
    if not os.path.exists(file_path):
        return
    with open(file_path, "r", encoding="utf-8") as file:
        module = ast.parse(file.read())
    logger.debug("Parsed module: %s", ast.dump(module))
    last_import_index = -1
    for i, stmt in enumerate(module.body):
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            last_import_index = i
    new_import_nodes = []
    for new_import in new_imports:
        parsed_import = ast.parse(new_import)
        logger.debug("Parsed import: %s", ast.dump(parsed_import))
        if len(parsed_import.body) >= 1:
            new_import_nodes.extend(parsed_import.body)
    logger.debug("New import nodes: %s", new_import_nodes)
    for new_import_node in new_import_nodes:
        if not any(
            (
                ast.dump(new_import_node) == ast.dump(existing_node)
                for existing_node in module.body
            )
        ):
            module.body.insert(last_import_index + 1, new_import_node)
            last_import_index += 1
    new_code = ast.unparse(module)
    logger.debug("New code: %s", new_code)
    new_code = format_code(new_code)
    logger.debug("Formatted code: %s", new_code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_code)


def format_code(code: str) -> str:
    """
    Format Python code using Black.

    Args:
        code (str): The code to format.

    Returns:
        str: The formatted code.
    """
    sorted_code = isort.code(code)
    return black.format_str(sorted_code, mode=black.FileMode(line_length=90))


def get_python_files(directory: str = ".", skip_tests: bool = True):
    """
    Get the paths of all the Python files in the present directory.

    Args:
        directory (str): The directory to search for Python files.
        skip_tests (bool): Whether to skip the 'tests' directory.

    Returns:
        list[str]: A list of paths to Python files.
    """
    python_files = []
    for root, dirs, files in os.walk(directory):
        if "tests" in dirs and skip_tests:
            dirs.remove("tests")
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if should_use_file(file_path):
                    python_files.append(file_path)
    logger.info("Found %s Python files.", len(python_files))
    logger.debug("Python files: %s", python_files)
    return python_files


def read_file_description(file_path: str) -> str:
    """
    Read the module docstring from a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        str: The module docstring.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read()
    module = ast.parse(contents)
    docstring = ast.get_docstring(module)
    return docstring


def read_function_description(function_code: str) -> str:
    """
    Read the docstring of a function.

    Args:
        function_code (str): The source code of the function.

    Returns:
        str: The docstring of the function.
    """
    function_as_module = ast.parse(function_code)
    function_def_nodes = [
        node for node in function_as_module.body if isinstance(node, ast.FunctionDef)
    ]
    if not function_def_nodes:
        return None
    function = function_def_nodes[0]
    docstring = ast.get_docstring(function)
    return docstring


def get_function_code(file_path: str, function_name: str) -> str:
    """
    Get the source code of a function from a Python file.

    Args:
        file_path (str): The path to the Python file.
        function_name (str): The name of the function.

    Returns:
        str: The source code of the function.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read()
    module = ast.parse(contents)
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            function_code = ast.get_source_segment(contents, node)
            return function_code
    return None


def add_docstring_to_function(file_path: str, function_name: str, docstring: str):
    """
    Add a docstring to a function.

    Args:
        file_path (str): The path to the Python file.
        function_name (str): The name of the function.
        docstring (str): The docstring to add.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        module = ast.parse(file.read())
    logger.debug("Parsed module: %s", ast.dump(module))
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
            break
    new_code = ast.unparse(module)
    logger.debug("New code: %s", new_code)
    new_code = format_code(new_code)
    logger.debug("Formatted code: %s", new_code)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_code)


