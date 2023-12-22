"""File to manage git operations for the repository."""

# Remember to routinely check subprocess calls for shell injection vulnerabilities
import subprocess  # nosec
from datetime import datetime
from typing import List
import shutil


class GitCommandError(Exception):
    """
    An error that occurs while executing a Git command.
    """


class GitHandler:
    """
    A handler for executing Git commands using the subprocess module.
    """

    def __init__(self):
        # Variable to store the names of temp branches
        self.temp_branches = list()
        # Variable to store the name of the branch that was checked out before the temp branch
        self.pre_temp_branch = None
        # Store git path
        self.git_path = shutil.which("git")

    @staticmethod
    def run_command(command: List[str]) -> None:
        """
        Run a git command using subprocess.

        Args:
            command (List[str]): The git command to run as a list of strings.

        Raises:
            GitCommandError: If the git command fails.
        """
        try:
            subprocess.check_output(command, shell=False)  # nosec - subprocess is not vulnerable to shell injection
        except subprocess.CalledProcessError as error:
            raise GitCommandError(
                f"An error occurred while running the git command: {' '.join(command)}"
            ) from error

    def create_new_branch(self, branch_name: str) -> None:
        """
        Create a new git branch.

        Args:
            branch_name (str): The name of the new branch.

        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command([self.git_path, "checkout", "-b", branch_name])

    def add_files(self) -> None:
        """
        Add all modified and new (untracked) files to git.

        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command([self.git_path, "add", "."])

    def commit_changes(self, commit_message: str) -> None:
        """
        Commit changes in git.

        Args:
            commit_message (str): The commit message.

        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command([self.git_path, "commit", "-m", commit_message])

    def push_changes(self, branch_name: str) -> None:
        """
        Push changes to a git branch.

        Args:
            branch_name (str): The name of the branch to push to.

        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command([self.git_path, "push", "origin", branch_name])

    def get_current_branch(self) -> str:
        """
        Get the name of the current branch.

        Returns:
            str: The name of the current branch.

        Raises:
            GitCommandError: If the git command fails.
        """
        return (
            subprocess.check_output(
                [self.git_path, "rev-parse", "--abbrev-ref", "HEAD"]
            )  # nosec B603
            .decode("utf-8")
            .strip()
        )

    def create_temp_test_branch(self, branch_name: str = None) -> str:
        """
        Create a new git branch.

        Args:
            branch_name (str): The name of the new branch.

        Returns:
            str: The name of the new branch.

        Raises:
            GitCommandError: If the git command fails.
        """
        current_branch = self.get_current_branch()
        if not branch_name:
            # Create branch with start of current branch name + _temp + timestamp
            branch_name = (
                current_branch + "_temp_" + datetime.now().strftime("%Y%m%d%H%M%S")
            )
        self.run_command([self.git_path, "checkout", "-b", branch_name])
        # Add branch to a class list to be deleted later
        self.temp_branches.append(branch_name)
        self.pre_temp_branch = current_branch
        return branch_name
