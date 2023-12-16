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
    parser.add_argument("--update_readme", action="store_true")
    parser.add_argument("--run_task_from_issues", action="store_true")
    parser.add_argument("--no_branch_and_commit", action="store_true")
    parser.add_argument("--populate_db", action="store_true")
    args = parser.parse_args()

    # Create new handler for git commands
    git_handler = GitHandler()

    if args.generate_tests:
        if not args.no_branch_and_commit:
            # Create a new branch for the tests
            git_handler.create_new_branch("generate_tests")
        core.generate_tests()
        if not args.no_branch_and_commit:
            # Add all files to git
            git_handler.add_files()
            # Commit changes
            git_handler.commit_changes("Auto add tests")

    if args.generate_module_docstrings:
        if not args.no_branch_and_commit:
            # Create a new branch for the docstrings
            git_handler.create_new_branch("generate_docstrings")
        core.generate_module_docstrings()
        if not args.no_branch_and_commit:
            # Add all files to git
            git_handler.add_files()
            # Commit changes
            git_handler.commit_changes("Auto add module docstrings")

    if args.format_modules:
        if not args.no_branch_and_commit:
            # Create a new branch for formatting the modules
            git_handler.create_new_branch("format_modules")
        core.format_modules()
        if not args.no_branch_and_commit:
            # Add all files to git
            git_handler.add_files()
            # Commit changes
            git_handler.commit_changes("Autoformat modules")

    if args.run_task:
        if not args.no_branch_and_commit:
            # Create a new branch for running the task
            git_handler.create_new_branch("run_task")
        core.run_task()
        if not args.no_branch_and_commit:
            # Add all files to git
            git_handler.add_files()
            # Commit changes
            git_handler.commit_changes("Auto run task")

    if args.update_readme:
        core.update_readme()

    if args.run_task_from_issues:
        core.run_task_from_next_issue()

    if args.populate_db:
        core.populate_db()
