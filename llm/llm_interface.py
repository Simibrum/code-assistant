"""
This script would handle interactions with the LLM, 
such as querying the LLM to generate new code or tests.
"""
import time
import random
from logging import Logger
import openai
from functions import logger

MODEL = "gpt-3.5-turbo"  # or whatever model you are using


def api_request(messages: list[dict], temperature: int = 0.7, gen_logger: Logger = logger):
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
                temperature=temperature
            )
            return response
        except Exception as e:
            if attempt == max_tries:
                gen_logger.error(f"API request failed - {attempt} attempts with final error {e}.")
                results = {"choices": [{"message": {"content": "ERROR: API request failed."}}]}
                return results

            delay = min(initial_delay * (backoff_factor ** (attempt - 1)), max_delay)
            jitter = random.uniform(jitter_range[0], jitter_range[1])
            sleep_time = delay + jitter
            gen_logger.error(
                f"API request failed. Error: {e}." 
                f"Retrying in {sleep_time:.2f} seconds."
            )
            time.sleep(sleep_time)

def generate_code(prompt: str, temperature: float = 0.7):
    """
    Use the LLM to generate Python code based on a given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.
        temperature (float, optional): The temperature parameter for the API request. 
        Default is 0.7.

    Returns:
        str: The generated Python code.
    """
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}]
    response = api_request(messages, temperature)
    return response['choices'][0]['message']['content']

def generate_test(prompt: str, temperature: float = 0.7):
    """
    Use the LLM to generate a Python test based on a given prompt.

    Args:
        prompt (str): The prompt to send to the LLM.
        temperature (float, optional): The temperature parameter for the API request. 
        Default is 0.7.

    Returns:
        str: The generated Python test.
    """
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}]
    response = api_request(messages, temperature)
    return response['choices'][0]['message']['content']
