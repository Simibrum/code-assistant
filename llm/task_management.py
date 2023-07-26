"""Functions to manage tasks."""
from typing import Tuple
import json
from llm.llm_interface import api_request, load_json_string
from llm import prompts
from functions import logger

TASK_FUNCTIONS = [
    {
        "name": "generate_function_for_task",
        "description": "Generate a python function to perform a task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_description": {
                    "type": "string",
                    "description": (
                        "Description of task to allow LLM to generate function "
                        "code in Python."
                    ),
                },
                "function_file": {
                    "type": "string",
                    "description": "Path to file where function will be written.",
                }
            },
            "required": ["task_description", "function_file"],
        },
    },
    {
        "name": "get_further_information",
        "description": "Get further information about a task from a user using chat.",
        "parameters": {
            "type": "object",
            "properties": {
                "questions_for_user": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": (
                        "List of strings containing questions to consecutively "
                        "ask the user to get further information."
                    ),
                }
            },
            "required": ["questions_for_user"],
        },
    },
    {
        "name": "divide_and_process_sub_tasks",
        "description": "Divide task into subtasks and process subtasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "sub_tasks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": (
                        "List of strings containing subtasks to be processed."
                    ),
                }
            },
            "required": ["sub_tasks"],
        },
    }
]

def process_task(task_description: str) -> Tuple[str, dict]:
    """Process a task description determine next action.

    Args:
        task_description (str): Description of task to be performed.

    Returns:
        str: Function name of next action to be performed.
        dict: Arguments to be passed to next action.
    """
    messages = prompts.build_messages(task_description)
    function_call = "auto"
    response = api_request(
        messages=messages, functions=TASK_FUNCTIONS, function_call=function_call
    )
    response_message = response["choices"][0]["message"]
    logger.debug("Response message: %s", response_message)
    if response_message.get("function_call"):
        function_to_call = response_message["function_call"]["name"]
        arguments_string = response_message["function_call"]["arguments"]
        # Tweak to prevent malformed escape sequences
        try:
            function_args = load_json_string(arguments_string)
        except json.JSONDecodeError as err:
            logger.debug("JSONDecodeError: %s", str(err))
            return None, None
        return function_to_call, function_args
    else:
        return response_message["content"], None
