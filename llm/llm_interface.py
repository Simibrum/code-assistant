"""
This script would handle interactions with the LLM, 
such as querying the LLM to generate new code or tests.
"""
import time
import random
from logging import Logger
import json
from typing import Tuple
import openai

from functions import logger
import llm.prompts as prompts


GOOD_MODEL = "gpt-4-0613"  # or whatever model you are using
QUICK_MODEL = "gpt-3.5-turbo-0613"

def load_json_string(s: str) -> dict:
    """
    Load a JSON string into a dictionary.

    Args:
        s (str): The JSON string to load.

    Returns:
        dict: The JSON string as a dictionary.
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError as err:
        logger.debug("JSONDecodeError: %s", str(err))
        # Fix triple escaped newlines
        s = s.replace('\\\n', '\\n')
        return json.loads(s)

def api_request(
    messages: list[dict],
    functions: list[dict],
    function_call: str | dict = "auto",
    temperature: int = 0.7,
    model: str = GOOD_MODEL,
    max_tokens: int = None,
    gen_logger: Logger = logger
):
    """
    Make a request to the OpenAI API with exponential backoff.

    Args:
        messages (List[dict]): A list of message objects for the Chat API.
        temperature (int, optional): The temperature parameter for the API request. Default is 0.7.
        gen_logger (Logger, optional): Logger for logging information about the API requests.

    Returns:
        dict: The API response as a dictionary.
    """
    max_tries = 5
    initial_delay = 1
    backoff_factor = 2
    max_delay = 16
    jitter_range = (1, 3)

    for attempt in range(1, max_tries + 1):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                functions=functions,
                function_call=function_call,
                max_tokens=max_tokens
            )
            return response
        except Exception as err:
            if attempt == max_tries:
                gen_logger.error(f"API request failed - {attempt} attempts with final error {err}.")
                results = {"choices": [{"message": {"content": "ERROR: API request failed."}}]}
                return results

            delay = min(initial_delay * (backoff_factor ** (attempt - 1)), max_delay)
            jitter = random.uniform(jitter_range[0], jitter_range[1])
            sleep_time = delay + jitter
            gen_logger.error("API request failed. Error: %s.", str(err))
            gen_logger.error("Retrying in %s seconds.", sleep_time)
            time.sleep(sleep_time)


CODE_FUNCTIONS = [
    {
        "name": "add_function_to_file",
        "description": "Add a new function to a Python file.",
        "parameters": {
            "type": "object",
            "properties": {
                "function_code": {
                    "type": "string",
                    "description": (
                        "Python code for the function to add, escaped. "
                        "Without imports - these are returned separately."
                    ),
                },
                "import_statements": {
                    "type": "string",
                    "description": "Python import statements for the function to add, escaped.",
                }
            },
            "required": ["function_code", "import_statements"],
        },
    }
]

def generate_from_prompt(prepare_prompt_func, prepare_prompt_args):
    """
    Use the LLM to generate Python code or a test based on a given prompt.

    Args:
        prepare_prompt_func (function): Function used to prepare the prompt.
        prepare_prompt_args (dict): Arguments to pass to the prepare prompt function.

    Returns:
        str: The generated Python code or test.
    """
    prompt = prepare_prompt_func(**prepare_prompt_args)
    messages = prompts.build_messages(prompt)
    function_call = {"name": "add_function_to_file"}
    response = api_request(
        messages=messages,
        functions=CODE_FUNCTIONS,
        function_call=function_call
    )
    response_message = response['choices'][0]['message']
    logger.debug("Response message: %s", response_message)
    if response_message.get('function_call'):
        arguments_string = response_message["function_call"]["arguments"]
        # Tweak to prevent malformed escape sequences
        try:
            function_args = load_json_string(arguments_string)
        except json.JSONDecodeError as err:
            logger.debug("JSONDecodeError: %s", str(err))
            return None, None
        imports = function_args.get("import_statements").split("\n")
        return function_args.get("function_code"), imports
    else:
        return response_message['content']

def generate_code(task_description: str, function_file: str) -> Tuple[str, str]:
    """
    Use the LLM to generate Python code for a given task.

    Args:
        task_description (str): A description of the task.

    Returns:
        str: The generated Python code.
        str: The generated import statements.
    """
    return generate_from_prompt(
        prompts.create_function_prompt,
        {"task_description": task_description, "function_file": function_file}
    )

def generate_test(function_code: str, function_file: str) -> Tuple[str, str]:
    """
    Use the LLM to generate a Python test based on a given prompt.

    Args:
        function_code (str): Code of function to build a test for.
        function_file (str): File containing the function to build a test for.

    Returns:
        Tuple[str, str]: A tuple containing the generated 
        Python test and import statements.
    """
    return generate_from_prompt(
        prompts.create_test_prompt,
        {"function_code": function_code, "function_file": function_file}
    )

def generate_module_docstring(module_code: str) -> str:
    """
    Use the LLM to generate a docstring for a Python module.

    Args:
        module_code (str): The source code of the module.

    Returns:
        str: The generated docstring.
    """
    prompt = prompts.create_module_docstring_prompt(module_code)
    messages = prompts.build_messages(prompt)
    response = api_request(
        messages=messages,
        functions=[],  # no functions required for this prompt
        function_call=None,
        model=QUICK_MODEL, 
        max_tokens=300
    )
    return response['choices'][0]['message']['content']
