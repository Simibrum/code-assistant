"""
This script would handle interactions with the LLM, 
such as querying the LLM to generate new code or tests.
"""
import time
import random
from logging import Logger
import json
import openai

from functions import logger
import llm.prompts as prompts


MODEL = "gpt-3.5-turbo-0613"  # or whatever model you are using


def api_request(
    messages: list[dict],
    functions: list[dict],
    function_call: str | dict = "auto",
    temperature: int = 0.7,
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
                model=MODEL,
                messages=messages,
                temperature=temperature,
                functions=functions,
                function_call=function_call,
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
                    "description": "Python code for the function to add.",
                },
                "import_statements": {
                    "type": "string",
                    "description": "Python import statements for the function to add.",
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
    if response_message.get('function_call'):
        function_args = json.loads(response_message["function_call"]["arguments"])
        return function_args.get("function_code")
    else:
        return response_message['content']

def generate_code(prompt: str):
    """
    Use the LLM to generate Python code based on a given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.

    Returns:
        str: The generated Python code.
    """
    return generate_from_prompt(lambda prompt: prompt, {"prompt": prompt})

def generate_test(function_code: str, function_file: str):
    """
    Use the LLM to generate a Python test based on a given prompt.

    Args:
        function_code (str): Code of function to build a test for.
        function_file (str): File containing the function to build a test for.

    Returns:
        str: The generated Python test.
    """
    return generate_from_prompt(
        prompts.create_test_prompt, 
        {"function_code": function_code, "function_file": function_file}
    )
