"""
Module to read information from the code files.
"""
from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import mapper, sessionmaker

import llm.llm_interface as llm
import utils


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
    function_descriptions = dict()
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
    all_function_descriptions = dict()
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

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker


class Code(object):
    def __init__(self, id=None, code_string=None):
        self.id = id
        self.code_string = code_string

    def __repr__(self):
        return f'<Code({self.id}, {self.code_string})>'


def setup_db(db_path='sqlite:///code.db'):
    """Set up an SQLite DB with SQLAlchemy to store code as strings.

    Args:
        db_path (str): The path to the SQLite DB. Defaults to 'sqlite:///code.db'.
    """
    engine = create_engine(db_path, echo=True)
    metadata = MetaData()
    code_table = Table('code', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('code_string', String),
                       )
    metadata.create_all(engine)
    mapper(Code, code_table)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
