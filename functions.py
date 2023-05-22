import os
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
import tiktoken


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