"""This module contains test functions for the `functions` module. 

The `test_load_env_vars` function tests the `load_env_vars` function, 
which loads environment variables from a file. It creates a temporary file 
with environment variable values, calls the function to load the variables, 
and checks if they are correctly loaded.

The `test_init_logger` function tests the `init_logger` function, 
which initializes a logger. It checks if the logger is properly initialized with the 
expected properties, such as the correct logger type, number of handlers, stream 
handler properties, formatter properties, and log level based on the debug mode.

The `test_num_tokens_from_messages` function tests the `num_tokens_from_messages` 
function, which calculates the number of tokens in a list of messages. It includes 
two test cases: one for the default model, where it verifies the expected number 
of tokens, and another for an unsupported model, where it raises a `NotImplementedError`.

These test functions ensure that the functions in the `functions` module are 
working correctly and provide proper test coverage."""
import logging
import os
import sys

import pytest

import functions


def test_load_env_vars(tmp_path):
    """
    Test the load_env_vars function from the functions module.
    """
    env_file = tmp_path / "test.env"
    env_file.write_text("VAR1=value1\nVAR2=value2\nVAR3=value3\n")
    functions.load_env_vars(env_file)
    assert os.getenv("VAR1") == "value1"
    assert os.getenv("VAR2") == "value2"
    assert os.getenv("VAR3") == "value3"
    assert os.getenv("VAR4") is None


def test_init_logger():
    """
    Test the init_logger function from the functions module.
    """
    logger = functions.init_logger()
    assert isinstance(logger, logging.Logger)
    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream == sys.stderr
    assert isinstance(logger.handlers[0].formatter, logging.Formatter)
    assert logger.handlers[0].formatter.datefmt == "%Y-%m-%d %H:%M:%S"
    debug_mode = os.environ.get("DEBUG_MODE", "False") == "True"
    if debug_mode:
        assert logger.level == logging.DEBUG
    else:
        assert logger.level == logging.INFO


def test_num_tokens_from_messages():
    """
    Test the num_tokens_from_messages function from the functions module.
    """
    messages = [
        {"role": "system", "content": "Hello"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm fine, thank you!"},
    ]
    assert functions.num_tokens_from_messages(messages) == 33
    with pytest.raises(NotImplementedError):
        messages = [
            {"role": "system", "content": "Hello"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm fine, thank you!"},
        ]
        functions.num_tokens_from_messages(messages, model="gpt-2.0-turbo")
