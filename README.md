# Coding Agent
A tool to help code with ChatGPT.

## Project Description

The aim is to build an agent that can code itself using an LLM. The LLM will return clear and concise Python code.
Simplicity is key. Functions will be returned with docstrings summarising the function. Python typing is to be used.
A test driven development strategy will be used. Testing is with pytest. Lines are limited to 100 characters.

## Auto Generated Summary

The project is a language learning model (LLM) based software development assistant, named 'Agent'. The Agent autonomously generates Python code, tests, and manages a GitHub repository. It uses multiple Python scripts to accomplish different tasks:
1. `utils.py`: Provides utility functions for the Agent such as extract project description from README, read a requirements.txt file, format Python code etc.
2. `agent.py`: It's the main script that conducts a loop where it determines the next tasks, performs them, and evaluates the results.
3. `functions.py`: Contains utility functions for loading environment variables, initializing a logger, and calculating the number of tokens used by a list of messages in a conversation.
4. `code_management`: This directory consists of various scripts responsible for managing the codebase. This includes generating test functions, reading information from code files, and handling writing code to Python files.
5. `llm`: This directory contains scripts for interacting with the LLM. It includes functions for generating prompts and communicating with the LLM to create new code or tests.

The Agent is designed to generate Python code, tests, and manage a GitHub repository autonomously, making it a valuable tool for automated software development.

## Agent Structure

```
/my_agent
    /llm
        llm_interface.py
    /code_management
        code_writer.py
        test_writer.py
    /github_management
        github_interface.py
    /actions
        run_tests.yml
    agent.py
    README.md
```
* `llm/llm_interface.py`: This script would handle interactions with the LLM, such as querying the LLM to generate new code or tests.
* `code_management/code_writer.py`: This script would handle writing code to your Python files, including adding new functions or refactoring existing ones.
* `code_management/test_writer.py`: This script would handle writing tests, such as adding new tests to your test files.
* `github_management/github_interface.py`: This script would handle interactions with GitHub, such as committing and pushing changes, creating new branches, or checking the status of GitHub Actions.
* `actions/run_tests.yml`: This is a GitHub Actions workflow file that's triggered on every push to run your tests.
* `agent.py`: This is the main script that uses all the other components to perform tasks. It would contain the main loop of the agent, where it determines the next task, performs the task, evaluates the result, and repeats.
* `README.md`: This is the README file for the agent's repository, explaining what the agent does and how to use it.

## Installation

## Usage

## To do

[X] - Build minimum agent structure
[ ] - Add function to add function docstrings
[ ] - Add function to read module docstrings for summary
[ ] - Add function to extract functions and their descriptions as a dict

## Contributing

## Testing

Performed via GitHub Actions.

## License

MIT License.

## Contact Information