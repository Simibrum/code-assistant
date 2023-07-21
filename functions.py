import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import tiktoken

import logging
from logging import Logger
import openai
import time
import random
import re

import os
import sys




def load_env_vars(path: str = ".env"):
    """Load environment variables from a file."""
    with open(path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                # Split the line into the variable name and value
                var, value = line.split("=")

                # Strip leading and trailing whitespace from the variable name and value
                var = var.strip()
                value = value.strip()

                if var and value:
                    # Set the environment variable
                    os.environ[var] = value

                    
def init_logger():
    """Initialise logger."""
    # Define module logger
    logger = logging.getLogger(__name__)
    # Initially set to log all - change this in production
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    # best for development or debugging
    consoleHandler = logging.StreamHandler(stream=sys.stderr)
    # create formatter - can also use %(lineno)d -
    # see https://stackoverflow.com/questions/533048/how-to-log-source-file-name-and-line-number-in-python/44401529
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s | %(filename)s > %(module)s > %(funcName)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # add formatter to ch and jh
    consoleHandler.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(consoleHandler)
    # Get logging level from environment variable - tweak to convert to boolean
    DEBUG_MODE = (os.environ.get('DEBUG_MODE', 'False') == 'True')
    if DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger, consoleHandler

# Initialise the logger
logger, consoleHandler = init_logger()

def read_gitignore(gitignore_path):
    with open(gitignore_path, "r") as file:
        gitignore_patterns = file.readlines()
    return [pattern.strip() for pattern in gitignore_patterns if pattern.strip()]


def build_directory_structure(start_path, gitignore_patterns=None, level=0, max_levels=None, indent="  "):
    if gitignore_patterns:
        pathspec = PathSpec.from_lines(GitWildMatchPattern, gitignore_patterns)

    if max_levels is not None and level > max_levels:
        return ""
    
    structure = ""
    for entry in os.listdir(start_path):
        path = os.path.join(start_path, entry)

        if gitignore_patterns and pathspec.match_file(path):
            continue
        
        # Also skip git config directories
        if entry in [".git", ".github", "__pycache__", ".pytest_cache"]:
            continue

        structure += indent * level + entry + "\n"
        
        if os.path.isdir(path):
            structure += build_directory_structure(path, gitignore_patterns, level+1, max_levels, indent)
            
    return structure


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
    See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


def read_requirements_txt(file_path):
    with open(file_path, "r") as file:
        contents = file.read()
    return contents

def build_messages(prompt, messages = None) -> list[dict]:
    """Build a set of chat messages based around the prompt as the last message."""
    if not messages:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": directory_prompt},
            {"role": "user", "content": requirements_prompt},
        ]
    messages += [{"role": "user", "content": prompt}]
    return messages
