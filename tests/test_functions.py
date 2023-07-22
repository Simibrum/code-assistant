
import os
import sys
import logging
import pytest
import functions


def test_load_env_vars(tmp_path):
    # Create a temporary file with environment variable values
    env_file = tmp_path / 'test.env'
    env_file.write_text('VAR1=value1\nVAR2=value2\nVAR3=value3\n')

    # Call the function to load the environment variables
    functions.load_env_vars(env_file)

    # Check if the environment variables are correctly loaded
    assert os.getenv('VAR1') == 'value1'
    assert os.getenv('VAR2') == 'value2'
    assert os.getenv('VAR3') == 'value3'
    assert os.getenv('VAR4') is None

def test_init_logger():
    # Test if logger is initialised correctly
    logger = functions.init_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)
    assert logger.handlers[0].stream == sys.stderr
    assert isinstance(logger.handlers[0].formatter, logging.Formatter)
    assert logger.handlers[0].formatter._fmt == (
        '%(asctime)s.%(msecs)03d - %(levelname)s - '
        '%(message)s | %(filename)s > %(module)s > %(funcName)s'
    )
    assert logger.handlers[0].formatter.datefmt == '%Y-%m-%d %H:%M:%S'
    assert logger.level == logging.DEBUG
    assert logger.level != logging.INFO

def test_num_tokens_from_messages():
    # Test case 1: Number of tokens with default model
    messages = [
        {"role": "system", "content": "Hello"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm fine, thank you!"}
    ]
    assert functions.num_tokens_from_messages(messages) == 40

    # Test case 2: Number of tokens with custom model
    messages = [
        {"role": "system", "content": "Hello"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm fine, thank you!"}
    ]
    assert functions.num_tokens_from_messages(messages, model="gpt-4.0-turbo") == 45

    # Test case 3: NotImplementedError for unsupported model
    with pytest.raises(NotImplementedError):
        messages = [
            {"role": "system", "content": "Hello"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm fine, thank you!"}
        ]
        functions.num_tokens_from_messages(messages, model="gpt-2.0-turbo")
