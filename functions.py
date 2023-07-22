import os
import sys

import logging
import tiktoken


def load_env_vars(path: str = ".env"):
    """Load environment variables from a file."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                # Split the line into the variable name and value
                var, value = line.split("=")

                # Strip leading and trailing whitespace from the variable name and value
                var = var.strip()
                value = value.strip()

                if var and value:
                    # Set the environment variable
                    os.environ[var] = value

                    
def init_logger():
    """Initialise logger."""
    # Define module logger
    loggerx = logging.getLogger(__name__)
    # Initially set to log all - change this in production
    loggerx.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    # best for development or debugging
    console_handler = logging.StreamHandler(stream=sys.stderr)
    # create formatter - can also use %(lineno)d -
    formatter = logging.Formatter(
        (
            '%(asctime)s.%(msecs)03d -'
            '%(levelname)s - %(message)s | %(filename)s > %(module)s > %(funcName)s'
        ),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # add formatter to ch and jh
    console_handler.setFormatter(formatter)
    # add ch to logger
    loggerx.addHandler(console_handler)
    # Get logging level from environment variable - tweak to convert to boolean
    debug_mode = (os.environ.get('DEBUG_MODE', 'False') == 'True')
    if debug_mode:
        loggerx.setLevel(logging.DEBUG)
    else:
        loggerx.setLevel(logging.INFO)
    return loggerx

# Initialise the logger
logger = init_logger()


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
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}.""")
