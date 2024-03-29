"""
Module to read information from the code files.
"""
import ast

from sqlalchemy.orm import Session

import llm.llm_interface as llm
import utils
from code_management.code_database import CodeClass, CodeFunction, CodeTest, link_tests
from functions import logger


def read_code_file_descriptions(start_dir: str) -> dict:
    """
    Read the descriptions of the code files in a directory.

    Args:
        start_dir (str): The path to the directory to read.

    Returns:
        dict: A dictionary mapping file paths to file descriptions.
    """
    code_file_descriptions = {}
    for file_path in utils.get_python_files(start_dir):
        code_file_descriptions[file_path] = utils.read_file_description(file_path)
    return code_file_descriptions


def read_function_descriptions(file_path: str) -> dict[str:str]:
    """
    Read the descriptions of the functions in a Python file.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        dict[str: str]: A dictionary of function name
         and function descriptions.
    """
    function_descriptions = {}
    for function_name, function_code in utils.extract_functions_from_file(file_path):
        function_descriptions[function_name] = utils.read_function_description(
            function_code
        )
    return function_descriptions


def read_all_function_descriptions(start_dir: str) -> dict[str : dict[str:str]]:
    """
    Read the descriptions of the functions in all Python files in a directory.

    Args:
        start_dir (str): The path to the directory to read.

    Returns:
        dict[str: dict[str: str]]: A dictionary of file paths and function descriptions.
    """
    all_function_descriptions = {}
    for file_path in utils.get_python_files(start_dir):
        all_function_descriptions[file_path] = read_function_descriptions(file_path)
    return all_function_descriptions


def generate_project_summary_prompt(code_file_descriptions, all_function_descriptions):
    """
    Generate a prompt for ChatGPT to create a project summary.

    Args:
        code_file_descriptions (dict): A dictionary mapping file paths to module docstrings.
        all_function_descriptions (dict): A dictionary mapping file paths to dictionaries,
            where the inner dictionaries map function names to function docstrings.

    Returns:
        str: The generated prompt.
    """
    prompt = "This project consists of several Python files, each with its own purpose, and several functions. "
    for file_path, module_description in code_file_descriptions.items():
        prompt += f"The file '{file_path}' is described as: '{module_description}'. "
    for file_path, function_descriptions in all_function_descriptions.items():
        prompt += f"In the file '{file_path}', there are several functions: "
        for function_name, function_description in function_descriptions.items():
            prompt += f"The function '{function_name}' is described as: '{function_description}'. "
    prompt += "Please provide a brief summary of the project as a whole."
    return prompt


def get_summary(start_directory: str) -> str:
    """Get a summary of the code in the project.

    Args:
        start_directory (str): The path to the directory to read.

    Returns:
        str: The summary of the code in the project."""
    code_file_descriptions = read_code_file_descriptions(start_directory)
    all_function_descriptions = read_all_function_descriptions(start_directory)
    prompt = generate_project_summary_prompt(
        code_file_descriptions, all_function_descriptions
    )
    summary = llm.generate_summary(prompt)
    return summary


def extract_classes_and_functions(
    contents: str,
) -> tuple[list[tuple[str, str, str, list[ast.AST]]], list[tuple[str, str, str]]]:
    """Extract classes and functions from a Python file.

    Args:
        contents (str): The contents of the Python file.

    Returns:
        tuple[list[tuple[str, str, str, list[ast.AST]]], list[tuple[str, str, str]]]:
            A tuple of classes and functions.
    """
    classes, functions = [], []
    module = ast.parse(contents)
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            class_string = ast.get_source_segment(contents, node)
            class_doc_string = ast.get_docstring(node) or ""
            classes.append((node.name, class_string, class_doc_string, node.body))
        elif isinstance(node, ast.FunctionDef):
            function_string = ast.get_source_segment(contents, node)
            function_doc_string = ast.get_docstring(node) or ""
            functions.append((node.name, function_string, function_doc_string))
    return classes, functions


def create_code_objects(session: Session, file_path: str):
    logger.info("Extracting classes and functions from %s", file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        contents = file.read()
    classes, functions = extract_classes_and_functions(contents)
    for class_params in classes:
        handle_class_processing(session, class_params, file_path, contents)
    for function_params in functions:
        handle_function_processing(session, function_params, file_path)
    session.commit()
    # Link tests to the functions they test
    link_tests(session)


def handle_class_processing(
    session: Session, class_params: tuple, file_path: str, contents: str
):
    class_name, class_string, class_doc_string, class_body = class_params
    existing_class = (
        session.query(CodeClass)
        .filter_by(class_name=class_name, file_path=file_path)
        .first()
    )
    if existing_class is None:
        logger.debug("Creating CodeClass object for %s", class_name)
        class_obj = CodeClass(
            class_string=class_string,
            class_name=class_name,
            file_path=file_path,
            doc_string=class_doc_string,
        )
        session.add(class_obj)
        session.commit()
        session.refresh(class_obj)
    else:
        class_obj = existing_class
    for node in class_body:
        if isinstance(node, ast.FunctionDef):
            handle_function_in_class_processing(
                session, node, file_path, contents, class_obj
            )


def handle_function_in_class_processing(
    session: Session,
    node: ast.FunctionDef,
    file_path: str,
    contents: str,
    class_obj: CodeClass,
):
    existing_function = (
        session.query(CodeFunction)
        .filter_by(
            function_name=node.name,
            file_path=file_path,
            code_class=class_obj,
        )
        .first()
    )
    if existing_function is None:
        logger.debug("Creating CodeFunction object for %s", node.name)
        function_string = ast.get_source_segment(contents, node)
        function_doc_string = ast.get_docstring(node) or ""
        function_obj = CodeFunction(
            function_string=function_string,
            function_name=node.name,
            file_path=file_path,
            doc_string=function_doc_string,
            code_class=class_obj,
            is_function=True,
        )
        session.add(function_obj)


def handle_function_processing(
    session: Session, function_params: tuple, file_path: str
):
    function_name, function_string, function_doc_string = function_params

    if _is_test(function_name, file_path):
        handle_test_function_processing(
            session, function_name, function_string, file_path, function_doc_string
        )
    else:
        handle_non_test_function_processing(
            session, function_name, function_string, file_path, function_doc_string
        )


def handle_test_function_processing(
    session: Session,
    function_name: str,
    function_string: str,
    file_path: str,
    function_doc_string: str,
):
    existing_test = (
        session.query(CodeTest)
        .filter_by(test_name=function_name, file_path=file_path)
        .first()
    )
    if existing_test is None:
        logger.debug("Creating CodeTest object for %s", function_name)
        test_obj = CodeTest(
            test_string=function_string,
            test_name=function_name,
            file_path=file_path,
            doc_string=function_doc_string,
        )
        session.add(test_obj)


def handle_non_test_function_processing(
    session: Session,
    function_name: str,
    function_string: str,
    file_path: str,
    function_doc_string: str,
):
    existing_function = (
        session.query(CodeFunction)
        .filter_by(function_name=function_name, file_path=file_path)
        .first()
    )
    if existing_function is None:
        logger.debug("Creating CodeFunction object for %s", function_name)
        function_obj = CodeFunction(
            function_string=function_string,
            function_name=function_name,
            file_path=file_path,
            doc_string=function_doc_string,
            is_function=True,
        )
        session.add(function_obj)


def _is_test(function_name: str, file_path: str) -> bool:
    return function_name.startswith("test_") or file_path.startswith("test_")
