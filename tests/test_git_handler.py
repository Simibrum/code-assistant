import pytest
import subprocess  # nosec
# from pytest import mocker

import git_management.git_handler
from git_management.git_handler import GitHandler


def test_GitHandler_run_command(mocker):
    """
    Test the run_command function to ensure it runs a git command and handles exceptions.

    Args:
        mocker: Pytest fixture that can be used to mock objects.

    """
    git_handler = GitHandler()
    mocked_check_output = mocker.patch("subprocess.check_output")
    git_handler.run_command(["git", "status"])
    mocked_check_output.assert_called_once_with(["git", "status"], shell=False)
    mocked_check_output.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="git status"
    )
    with pytest.raises(git_management.git_handler.GitCommandError) as exc_info:
        git_handler.run_command(["git", "status"])
    assert "An error occurred while running the git command: git status" in str(
        exc_info.value
    )


def test_GitHandler_create_new_branch(mocker):
    """
    Test the create_new_branch function of GitHandler to ensure it runs the correct command.
    """
    git_handler = GitHandler()
    branch_name = "feature/new-branch"
    expected_command = ["git", "checkout", "-b", branch_name]
    mocker.patch.object(git_handler, "run_command")
    git_handler.create_new_branch(branch_name)
    git_handler.run_command.assert_called_once_with(expected_command)


def test_GitHandler_add_files(mocker):
    """
    Test the GitHandler.add_files method to ensure it adds all modified and new files.
    """
    git_handler = GitHandler()  # Instantiate the real class
    git_handler.run_command = mocker.Mock()  # Mock only the run_command method
    git_handler.add_files()
    git_handler.run_command.assert_called_once_with(["git", "add", "."])


def test_GitHandler_push_changes(mocker):
    """
    Test the push_changes method in GitHandler to ensure it calls the correct git command.

    Args:
        mocker: A pytest-mock fixture used to mock objects and functions.
    """
    # Arrange
    from git_management.git_handler import GitHandler

    git_handler = GitHandler()
    branch_name = "feature-branch"
    mock_run_command = mocker.patch.object(git_handler, "run_command")

    # Act
    git_handler.push_changes(branch_name)

    # Assert
    mock_run_command.assert_called_once_with(["git", "push", "origin", branch_name])
