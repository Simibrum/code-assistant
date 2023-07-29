"""File to manage git operations for the repository."""

import subprocess
from typing import List

class GitCommandError(Exception):
    """
    An error that occurs while executing a Git command.
    """


class GitHandler:
    """
    A handler for executing Git commands using the subprocess module.
    """

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
            subprocess.check_output(command)
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
        self.run_command(["git", "checkout", "-b", branch_name])

    def add_files(self) -> None:
        """
        Add all modified and new (untracked) files to git.
        
        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command(["git", "add", "."])

    def commit_changes(self, commit_message: str) -> None:
        """
        Commit changes in git.

        Args:
            commit_message (str): The commit message.
        
        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command(["git", "commit", "-m", commit_message])

    def push_changes(self, branch_name: str) -> None:
        """
        Push changes to a git branch.

        Args:
            branch_name (str): The name of the branch to push to.
        
        Raises:
            GitCommandError: If the git command fails.
        """
        self.run_command(["git", "push", "origin", branch_name])
