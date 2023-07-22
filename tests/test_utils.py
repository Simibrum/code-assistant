"""Tests for the utils module. """
import tempfile
import os
import utils


def test_extract_functions_from_file():
    """Test the extract_functions_from_file function."""
    # Define a simple Python code with two functions.
    code = '''
def func1(a, b):
    return a + b

def func2(x):
    return x * 2
'''

    # Create a temporary file and write the code to it.
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(code)
        temp_path = temp.name

    # Call extract_functions_from_file with the path of the temporary file.
    functions = utils.extract_functions_from_file(temp_path)

    # Check that the correct functions were extracted.
    assert len(functions) == 2
    assert (functions[0][0] == 'func1' and 'def func1(a, b):' in functions[0][1])
    assert (functions[1][0] == 'func2' and 'def func2(x):' in functions[1][1])

    # Cleanup: remove the temporary file.
    os.remove(temp_path)
