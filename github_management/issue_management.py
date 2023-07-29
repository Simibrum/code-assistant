"""File to manage issues on GitHub for the repository."""
import os
from github import Github


GITHUB_TOKEN = os.environ.get('TOKEN_GH')

class IssueAlreadyExistsError(Exception):
    """Raised when an issue with the same title already exists."""


class GitHubIssues:
    """Class to manage issues on GitHub for the repository."""
    def __init__(self, token: str, repo_name: str):
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def get_open_issues(self):
        """Fetch the open issues for the repository."""
        open_issues = self.repo.get_issues(state='open')
        return open_issues

    def get_all_issues(self):
        """Fetch all issues for the repository."""
        issues = self.repo.get_issues()
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
                raise IssueAlreadyExistsError("Issue with the same title already exists.")
        self.repo.create_issue(title=title, body=body)
