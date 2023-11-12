"""This module provides utility functions for loading environment variables and initializing a logger. It also includes a function to calculate the number of tokens used by a list of messages in a conversation.

The `load_env_vars` function takes an optional `path` parameter to specify the file path of the environment variable file. It reads the file and sets the environment variables accordingly.

The `init_logger` function initializes a logger with the name of the current module. It sets the logger level to `DEBUG` by default, but can be changed to `INFO` based on the value of the `DEBUG_MODE` environment variable. It also configures the logger to log to the console.

The `num_tokens_from_messages` function calculates the number of tokens used by a list of messages in a conversation. It accepts the `messages` list and an optional `model` parameter to specify the model to use. It uses the `tiktoken` library to encode the message content and counts the tokens used based on the encoding scheme.

Please note that the `num_tokens_from_messages` function is currently implemented only for the "gpt-3.5-turbo-0301" model. For other models, a `NotImplementedError` is raised.

The module also includes a pre-initialized logger named `logger`.

This module can be used to load environment variables, initialize a logger, and calculate the number of tokens used in a conversation."""
import logging
import os
import sys

import tiktoken


def load_env_vars(path: str = ".env"):
    """Load environment variables from a file."""
    with open(path, encoding="utf-8") as file:
        for line in file:
            if "=" in line and (not line.startswith("#")):
                var, value = line.split("=")
                var = var.strip()
                value = value.strip()
                if var and value:
                    os.environ[var] = value


def init_logger():
    """Initialise logger."""
    loggerx = logging.getLogger(__name__)
    loggerx.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d -%(levelname)s - %(message)s | %(filename)s > %(module)s > %(funcName)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    loggerx.addHandler(console_handler)
    debug_mode = os.environ.get("DEBUG_MODE", "False") == "True"
    if not debug_mode:
        loggerx.setLevel(logging.INFO)
    return loggerx


logger = init_logger()


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += -1
            num_tokens += 2
        return num_tokens
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not presently implemented for model {model}."
        )
