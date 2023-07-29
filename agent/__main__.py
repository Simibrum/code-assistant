"""File that runs the agent."""
import argparse
import agent.core as core
from git_management.git_handler import GitHandler


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate_tests", action="store_true")
    parser.add_argument("--generate_module_docstrings", action="store_true")
    parser.add_argument("--format_modules", action="store_true")
    parser.add_argument("--run_task", action="store_true")
    args = parser.parse_args()

    # Create new handler for git commands
    git_handler = GitHandler()

    if args.generate_tests:
        # Create a new branch for the tests
        git_handler.create_new_branch("generate_tests")
        core.generate_tests()
        # Add all files to git
        git_handler.add_files()
        # Commit changes
        git_handler.commit_changes("Add tests")


    if args.generate_module_docstrings:
        # Create a new branch for the docstrings
        git_handler.create_new_branch("generate_docstrings")
        core.generate_module_docstrings()
        # Add all files to git
        git_handler.add_files()
        # Commit changes
        git_handler.commit_changes("Add module docstrings")

    if args.format_modules:
        # Create a new branch for formatting the modules
        git_handler.create_new_branch("format_modules")
        core.format_modules()
        # Add all files to git
        git_handler.add_files()
        # Commit changes
        git_handler.commit_changes("Format modules")

    if args.run_task:
        # Create a new branch for running the task
        git_handler.create_new_branch("run_task")
        core.run_task()
        # Add all files to git
        git_handler.add_files()
        # Commit changes
        git_handler.commit_changes("Run task")
