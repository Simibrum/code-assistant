

import json
import pytest
from llm.task_management import process_task
from unittest.mock import patch


def test_process_task():
    """Test the process_task function."""
    # Mocking the returned value of api_request
    with patch('llm.task_management.api_request') as mock_request:
        # Mocking the returned value of load_json_string
        with patch('llm.task_management.load_json_string') as mock_json:
            mock_request.return_value = {
                'choices': [{'message': {'function_call': {'name': 'function_to_call', 'arguments': 'arguments_string'}}}]}
            mock_json.return_value = 'function_args'

            function_to_call, function_args = process_task('task_description')
            assert function_to_call == 'function_to_call'
            assert function_args == 'function_args'

            # Test when JSONDecodeError is raised
            mock_json.side_effect = json.JSONDecodeError('Mocked error', 'doc', 0)
            result = process_task('task_description')
            assert result == (None, None)

            # Test when 'function_call' is not in response_message
            mock_request.return_value = {'choices': [{'message': {'content': 'mocked_content'}}]}
            result = process_task('task_description')
            assert result == ('mocked_content', None)

