# Coding Agent

A tool to help code with ChatGPT.

## Project Description

The aim is to build an agent that can code itself using an LLM. The LLM will return clear and concise Python code.
Simplicity is key. Functions will be returned with docstrings summarising the function. Python typing is to be used.
A test driven development strategy will be used. Testing is with pytest. Lines are limited to 100 characters.

## Auto Generated Summary

The project is a language learning model (LLM) based software development assistant, named 'Agent'. The Agent autonomously generates Python code, tests, and manages a GitHub repository. It uses multiple Python scripts to accomplish different tasks:

1. `utils.py`: Provides utility functions for the Agent such as extract project description from README, read a requirements.txt file, format Python code etc.
1. `agent.py`: It's the main script that conducts a loop where it determines the next tasks, performs them, and evaluates the results.
1. `functions.py`: Contains utility functions for loading environment variables, initializing a logger, and calculating the number of tokens used by a list of messages in a conversation.
1. `code_management`: This directory consists of various scripts responsible for managing the codebase. This includes generating test functions, reading information from code files, and handling writing code to Python files.
1. `llm`: This directory contains scripts for interacting with the LLM. It includes functions for generating prompts and communicating with the LLM to create new code or tests.

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

- `llm/llm_interface.py`: This script would handle interactions with the LLM, such as querying the LLM to generate new code or tests.
- `code_management/code_writer.py`: This script would handle writing code to your Python files, including adding new functions or refactoring existing ones.
- `code_management/test_writer.py`: This script would handle writing tests, such as adding new tests to your test files.
- `github_management/github_interface.py`: This script would handle interactions with GitHub, such as committing and pushing changes, creating new branches, or checking the status of GitHub Actions.
- `actions/run_tests.yml`: This is a GitHub Actions workflow file that's triggered on every push to run your tests.
- `agent.py`: This is the main script that uses all the other components to perform tasks. It would contain the main loop of the agent, where it determines the next task, performs the task, evaluates the result, and repeats.
- `README.md`: This is the README file for the agent's repository, explaining what the agent does and how to use it.

## Installation

## Usage

## To do

Loaded from repository [Issues](https://github.com/Simibrum/code-assistant/issues):

- \[ \] Useful links and resources
- \[ \] Test Generation for Classes
- \[ \] Write "Agent Structure" Section of Readme.MD Automatically
- \[ \] Write "To Do" Section of Readme Automatically Based on GitHub Issues
- \[ \] Complete the Agent Process for Generating New Code
- \[ \] Have Requests for More Information in Issue Comments

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

Performed via GitHub Actions.

## License

MIT License.

## Contact Information
