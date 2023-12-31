# Coding Agent

A tool to help code with ChatGPT.

## Project Description

The aim is to build an agent that can code itself using an LLM. 

The LLM will return clear and concise Python code.
Simplicity is key. Functions will be returned with docstrings summarising the function. Python `typing` is to be used.
A test driven development strategy will be used. Testing is with `pytest`. Lines are limited to 100 characters.

## Auto Generated Summary

The project aims to build a self-coding agent that utilizes a Language Learning Model (LLM) to generate code, tests, and manage a GitHub repository. The agent operates through several Python files each with its own purpose and functions. Some key functions involve extracting project descriptions from README files, loading environment variables, initializing a logger, calculating the number of tokens used in a conversation, managing GitHub issues, reading information from code files, writing code to Python files, and parsing and manipulating Markdown files, among others.

The agent also interacts with the LLM to generate new code or tests, create function prompts, and manage tasks. It has capabilities to generate docstrings for modules and functions, produce to-do lists, and summarize project code. It uses pytest for testing and includes functionalities to analyze test results and improve code based on these analyses.

Overall, the project represents an advanced use case of AI in automating the software development process, contributing to coding efficiency and quality.

## Agent Structure

```
github_management
  branch_management.py
  issue_management.py
temp_test_results.json
utils.py
code_management
  __init__.py
  test_writer.py
  code_reader.py
  code_writer.py
  readme_manager.py
.devcontainer
  devcontainer.json
requirements.txt
LICENSE
llm
  __init__.py
  prompts.py
  task_management.py
  llm_interface.py
git_management
  __init__.py
  git_handler.py
agent
  test_analysis.py
  __init__.py
  core.py
  __main__.py
tests
  test_functions.py
  __init__.py
  test_prompts.py
  test_readme_manager.py
  test_code_reader.py
  test_test_analysis.py
  test_core.py
  test_utils.py
  test_llm_interface.py
  test_code_writer.py
  test_agent.py
  test_task_management.py
.gitignore
functions.py
.vscode
  settings.json
pyproject.toml
README.md

```

The following files are included in the repository:

- `./utils.py`: `utils.py` - Provides utility functions for the Agent.
- `./functions.py`: Provides utility functions for loading environment variables, initializing a logger, and calculating the number of tokens used by a list of messages in a conversation.
- `./github_management/branch_management.py`: None
- `./github_management/issue_management.py`: File to manage issues on GitHub for the repository.
- `./code_management/__init__.py`: None
- `./code_management/test_writer.py`: Code for generating test functions.
- `./code_management/code_reader.py`: Module to read information from the code files.
- `./code_management/code_writer.py`: Handles writing code to Python files, including adding new functions or refactoring existing ones.
- `./code_management/readme_manager.py`: Provides functions for parsing and manipulating Markdown files, including parsing a README.md file, retrieving the contents of a specific section, extracting headings, and replacing text in a Markdown document between headings.
- `./llm/__init__.py`: None
- `./llm/prompts.py`: Common prompt building functions.
- `./llm/task_management.py`: Functions to manage tasks.
- `./llm/llm_interface.py`: Handles interactions with the LLM, such as querying it to generate new code or tests.
- `./git_management/__init__.py`: None
- `./git_management/git_handler.py`: File to manage git operations for the repository.
- `./agent/test_analysis.py`: Functions to analyze test results and improve the code.
- `./agent/__init__.py`: Package for agent functions.
- `./agent/core.py`: The main script that uses all the other components to perform tasks, including determining the next task, performing it, evaluating the result, and repeating.
- `./agent/__main__.py`: File that runs the agent.

## Installation

## Usage

## To do

Loaded from repository [Issues](https://github.com/Simibrum/code-assistant/issues):

- \[X\] Create WebInterface.py
- \[ \] Test Generation for Classes
- \[ \] Write "Agent Structure" Section of Readme.MD Automatically
- \[X\] Write "To Do" Section of Readme Automatically Based on GitHub Issues
- \[ \] Complete the Agent Process for Generating New Code
- \[ \] Have Requests for More Information in Issue Comments
- \[X\] Generate tests

## GitHub Integration

GitHub has good resources to manage a coding project. We will make use of them.

What is the best way to connect to the repository data? Github App, OAuth app or Personal Access Token?

Create an access token (here's howto - https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

If you are working with an organisation repository there are a few extra steps:

- Turn on organisation level personal access tokens (PAT) - https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/setting-a-personal-access-token-policy-for-your-organization
- As an individual developer who has access to organisation resources, create a new PAT restricting to access to the organisation repository
- Add as a Codespace secret for the repository

## Contributing

## Testing

Pre-commit hooks are used to run tests before committing. Tests are run using pytest.

Pre-commit hooks are run using pre-commit. To install pre-commit, run `pip install pre-commit`. To install the
pre-commit hooks, run `pre-commit install`.
The hooks are as follows:

* `black`: Runs black to format the code.
* `flake8`: Runs flake8 to lint the code.
* `pylint`: Runs pylint to lint the code (again but covering different aspects).
* `bandit`: Runs bandit to check for security issues.
* `pydocstyle`: Runs pydocstyle to check docstrings.

Run `pre-commit autoupdate` to update the hooks.
Run `pre-commit run --all-files` to run the hooks on all files.
Run `pre-commit run --all-files > pre_commit_results.txt 2>&1` to log the output to a file.

Testing with Pytest is performed via GitHub Actions.

## License

MIT License.

## Contact Information
