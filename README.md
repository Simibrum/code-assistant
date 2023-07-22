# Coding Agent
A tool to help code with ChatGPT.

## Project Description

The aim is to build an agent that can code itself using an LLM. The LLM will return clear and concise Python code.
Simplicity is key. Functions will be returned with docstrings summarising the function. Python typing is to be used.
A test driven development strategy will be used. Testing is with pytest. Lines are limited to 100 characters.

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

[ ] - Build minimum agent structure

## Contributing

## Testing

Performed via GitHub Actions.

## License

MIT License.

## Contact Information
