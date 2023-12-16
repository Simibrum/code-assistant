"""File to manage issues on GitHub for the repository.

See https://pygithub.readthedocs.io/ for documentation on the GitHub API wrapper.
"""
import re

from github import Github

import llm.llm_interface as llm
from config import GITHUB_TOKEN


class IssueAlreadyExistsError(Exception):
    """Raised when an issue with the same title already exists."""


def slugify(title, max_length=30):
    """Converts a title to a slug."""
    slug = re.sub(r"[^\w\s-]", "", title)  # Remove non-alphanumeric characters
    slug = re.sub(r"\s+", "_", slug)  # Replace spaces and hyphens with underscores
    return slug[:max_length]


class GitHubIssues:
    """Class to manage issues on GitHub for the repository."""

    def __init__(
        self, token: str = GITHUB_TOKEN, repo_name: str = "simibrum/code-assistant"
    ):
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def get_open_issues(self):
        """Fetch the open issues for the repository."""
        open_issues = self.repo.get_issues(state="open")
        return open_issues

    def get_all_issues(self):
        """Fetch all issues for the repository."""
        issues = self.repo.get_issues(state="all", sort="created", direction="asc")
        return issues

    def print_issue_details(self, issue):
        """Print details for a given issue."""
        print(f"Issue Number: {issue.number}")
        print(f"Title: {issue.title}")
        print(f"Body: {issue.body}")
        print(f"Created at: {issue.created_at}")
        print(f"Updated at: {issue.updated_at}")
        print(f"State: {issue.state}")
        print(f"Comments: {issue.comments}")
        print("------------")

    def generate_branch_name(self, issue):
        """Generate a branch name for a given issue."""
        issue_number = issue.number
        issue_title_slug = slugify(issue.title)
        branch_name = f"issue_{issue_number}_{issue_title_slug}"
        return branch_name

    def print_all_open_issue_details(self):
        """Fetch and print details of all open issues."""
        open_issues = self.get_open_issues()
        for issue in open_issues:
            if issue.pull_request is None:
                self.print_issue_details(issue)

    def create_issue(self, title: str, body: str):
        """Create an issue for the repository."""
        # Check if there's an issue with the same title
        issues = self.get_all_issues()
        for issue in issues:
            if issue.title == title:
                raise IssueAlreadyExistsError(
                    "Issue with the same title already exists."
                )
        self.repo.create_issue(title=title, body=body)

    def add_label_to_issue(self, issue_number: int, label_name: str):
        """Add a label to an issue."""
        issue = self.repo.get_issue(issue_number)
        # Check if the label already exists
        issue.add_to_labels(label_name)

    def select_easiest_issue(self, token_limit: int = 3800):
        """Use an LLM to determine the easiest issue to solve."""
        open_issues = self.get_open_issues()

        issue_number = llm.review_issues(open_issues, token_limit)

        # Assign the label 'next-to-do' to the selected issue
        self.add_label_to_issue(issue_number, "next-to-do")

    def get_next_issue(self):
        """Fetch the next issue to work on."""
        next_to_do_issues = self.repo.get_issues(labels=["next-to-do"])
        if not list(next_to_do_issues):
            self.select_easiest_issue()
            next_to_do_issues = self.repo.get_issues(labels=["next-to-do"])
        # Get the first issue in the list
        issues = list(next_to_do_issues)
        if issues:
            return issues[0]
        else:
            return None

    def task_from_issue(self, issue) -> str:
        """Create a task description from an issue."""
        task_description = (
            f"* Task from Issue #{issue.number}: {issue.title}\n{issue.body}\n----\n"
        )
        return task_description
