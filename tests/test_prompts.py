def test_get_directory_prompt():
    # Test case 1
    start_path = '/path/to/start'
    git_ignore_path = '/path/to/gitignore'
    expected_prompt = 'The directory structure for the project is: ...'
    assert get_directory_prompt(start_path, git_ignore_path) == expected_prompt
    
    # Test case 2
    start_path = '/another/path'
    git_ignore_path = '/another/gitignore'
    expected_prompt = 'The directory structure for the project is: ...'
    assert get_directory_prompt(start_path, git_ignore_path) == expected_prompt
    
def test_get_installed_packages_prompt():
    # Test case 1
    requirements_path = 'path/to/requirements.txt'
    expected_prompt = "The installed packages as set out in `requirements.txt` are:\npackage1\npackage2\npackage3"
    assert get_installed_packages_prompt(requirements_path) == expected_prompt

    # Test case 2
    requirements_path = 'path/to/empty_requirements.txt'
    expected_prompt = "The installed packages as set out in `requirements.txt` are:\n"
    assert get_installed_packages_prompt(requirements_path) == expected_prompt
