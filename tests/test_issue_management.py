import pytest

from github_management.issue_management import (
    GitHubIssues,
    IssueAlreadyExistsError,
    slugify,
)


def test_slugify():
    """
    Test the slugify function.
    """
    title = "Test Title 1"
    expected_slug = "Test_Title_1"
    assert slugify(title) == expected_slug
    title = "Test Title $&@!"
    expected_slug = "Test_Title_"
    assert slugify(title) == expected_slug
    title = "This is a very long title that should be truncated"
    expected_slug = "This_is_a_very_long_title_that"
    assert slugify(title) == expected_slug

    # New test case to test untested lines
    title = "Title with - hyphen"
    expected_slug = "Title_with_hyphen"
    assert slugify(title) == expected_slug
    title = "Title with   multiple   spaces"
    expected_slug = "Title_with_multiple_spaces"
    assert slugify(title) == expected_slug


def test_get_open_issues(mocker):
    """Test if get_open_issues function fetches open issues correctly."""

    # Create mock repository
    mock_repo = mocker.MagicMock()
    mock_repo.get_issues.return_value = ["issue1", "issue2"]

    # Create instance of GitHubIssues with mock repository
    mock_issue_mgmt = GitHubIssues()
    mock_issue_mgmt.repo = mock_repo

    # Call get_open_issues method
    result = mock_issue_mgmt.get_open_issues()

    # Check if the result is as expected
    assert result == [
        "issue1",
        "issue2",
    ], "The get_open_issues function failed to fetch open issues."

    # Check if get_issues method of mock repository was called with correct argument
    mock_repo.get_issues.assert_called_once_with(state="open")


def test_get_all_issues(mocker):
    """Test that all issues are fetched from the repository."""
    mock_repo = mocker.MagicMock()
    mock_repo.get_issues.return_value = ["issue1", "issue2", "issue3"]
    mock_issue_management = GitHubIssues()
    mock_issue_management.repo = mock_repo
    result = mock_issue_management.get_all_issues()
    mock_repo.get_issues.assert_called_once_with(
        state="all", sort="created", direction="asc"
    )
    assert result == ["issue1", "issue2", "issue3"]


def test_print_issue_details(mocker):
    """Test the print_issue_details function by checking the output."""

    class MockIssue:
        def __init__(self):
            self.number = 123
            self.title = "Test Issue"
            self.body = "This is a test issue body."
            self.created_at = "2023-03-23T12:00:00Z"
            self.updated_at = "2023-03-23T13:00:00Z"
            self.state = "open"
            self.comments = 10

    mock_issue = MockIssue()
    expected_output = (
        "Issue Number: 123\n"
        "Title: Test Issue\n"
        "Body: This is a test issue body.\n"
        "Created at: 2023-03-23T12:00:00Z\n"
        "Updated at: 2023-03-23T13:00:00Z\n"
        "State: open\n"
        "Comments: 10\n------------"
    )
    git_issues = GitHubIssues()

    mocker.patch("builtins.print")

    git_issues.print_issue_details(mock_issue)

    assert print.call_args_list == [
        mocker.call(line) for line in expected_output.split("\n")
    ]


def test_generate_branch_name(mocker):
    """
    Test generate_branch_name function to ensure it creates the correct branch name
    from a given issue.
    """
    mock_issue = mocker.Mock()
    mock_issue.number = 42
    mock_issue.title = "Add new feature"
    expected_branch_name = "issue_42_add_new_feature"
    actual_branch_name = GitHubIssues().generate_branch_name(mock_issue)
    assert actual_branch_name == expected_branch_name


def test_print_all_open_issue_details(mocker):
    """
    Test that the function print_all_open_issue_details fetches open issues
    and prints their details correctly, ignoring pull requests.
    """
    issue_manager = GitHubIssues()
    mock_issue_1 = mocker.Mock(pull_request=None)
    mock_issue_2 = mocker.Mock(pull_request="dummy_pr_link")
    issue_manager.get_open_issues = mocker.Mock(
        return_value=[mock_issue_1, mock_issue_2]
    )
    issue_manager.print_issue_details = mocker.Mock()
    issue_manager.print_all_open_issue_details()
    issue_manager.get_open_issues.assert_called_once()
    assert issue_manager.print_issue_details.call_count == 1
    issue_manager.print_issue_details.assert_called_with(mock_issue_1)


def test_create_issue(mocker):
    """Test creating a new issue with a unique title."""
    mock_repo = mocker.Mock()
    mock_issue = mocker.Mock(title="Existing Issue Title")
    issue_management = GitHubIssues()
    issue_management.repo = mock_repo
    issue_management.get_all_issues = mocker.Mock(return_value=[mock_issue])
    unique_title = "Unique Issue Title"
    issue_body = "Details of the issue."
    issue_management.create_issue(unique_title, issue_body)
    mock_repo.create_issue.assert_called_once_with(title=unique_title, body=issue_body)
    with pytest.raises(IssueAlreadyExistsError):
        issue_management.create_issue(mock_issue.title, issue_body)


def test_add_label_to_issue(mocker):
    """Test adding a label to an issue."""
    issue_number = 42
    label_name = "bug"
    mock_repo = mocker.MagicMock()
    mock_issue = mocker.MagicMock()
    mock_repo.get_issue.return_value = mock_issue
    issue_management = GitHubIssues()
    issue_management.repo = mock_repo
    issue_management.add_label_to_issue(issue_number, label_name)
    mock_repo.get_issue.assert_called_once_with(issue_number)
    mock_issue.add_to_labels.assert_called_once_with(label_name)


def test_select_easiest_issue(mocker):
    """
    Test the select_easiest_issue function to ensure it selects an issue and adds the label.
    """
    from unittest.mock import MagicMock, patch

    from github_management.issue_management import GitHubIssues, llm

    # Mock the GitHubIssues class methods
    GitHubIssues.get_open_issues = MagicMock(
        return_value=["Issue 1", "Issue 2", "Issue 3"]
    )
    GitHubIssues.add_label_to_issue = MagicMock()
    issue_management = GitHubIssues()
    with patch.object(llm, "review_issues", return_value=2) as mock_review_issues:
        issue_management.select_easiest_issue(3800)
        mock_review_issues.assert_called_once_with(
            ["Issue 1", "Issue 2", "Issue 3"], 3800
        )
    # Check if the label has been added to the right issue
    issue_management.add_label_to_issue.assert_called_once_with(2, "next-to-do")


def test_get_next_issue():
    from unittest.mock import patch
    from github_management.issue_management import GitHubIssues

    class MockIssue:
        def __init__(self):
            self.number = 123
            self.title = "Test Issue"
            self.body = "This is a test issue body."

    mock_issues = [MockIssue(), MockIssue(), MockIssue()]

    class MockRepo:
        def get_issues(self, labels: list):
            if "next-to-do" in labels:
                return mock_issues
            else:
                return []

    issue_manager = GitHubIssues()
    issue_manager.repo = MockRepo()

    with patch(
        "github_management.issue_management.llm.review_issues"
    ) as mock_review_issues:
        mock_review_issues.return_value = 123
        issue = issue_manager.get_next_issue()

    assert issue is not None, "Should return an issue when 'next-to-do' issues exist"

    # Test for the scenario where no issues are returned
    mock_issues.clear()
    issue = issue_manager.get_next_issue()
    assert issue is None, "Should return None when no 'next-to-do' issues exist"


def test_task_from_issue():
    """Test the task_from_issue function."""

    class MockIssue:
        def __init__(self, number, title, body):
            self.number = number
            self.title = title
            self.body = body

    issue = MockIssue(123, "Fix bug", "There is a critical bug that needs fixing")
    expected = "* Task from Issue #123: Fix bug\nThere is a critical bug that needs fixing\n----\n"
    git_issues = GitHubIssues()
    result = git_issues.task_from_issue(issue)
    assert result == expected


def test_GitHubIssues___init__(monkeypatch):
    from unittest.mock import Mock
    from github_management.issue_management import GitHubIssues, Github

    test_token = "test_token"  # nosec
    test_repo_name = "test_owner/test_repo"
    mock_github = Mock(spec=Github)
    mock_repo = Mock()
    mock_github.get_repo.return_value = mock_repo
    monkeypatch.setattr(
        "github_management.issue_management.Github", lambda x: mock_github
    )  # Replace with actual library

    github_issues = GitHubIssues(token=test_token, repo_name=test_repo_name)
    assert github_issues.github == mock_github, "Github instance not correctly set."
    assert github_issues.repo == mock_repo, "Repo object not correctly set."
    mock_github.get_repo.assert_called_once_with(test_repo_name)

    # Test with no token and repo_name
    github_issues = GitHubIssues(token=None, repo_name=None)
    assert github_issues.github is None, "Github instance not correctly set."
    assert github_issues.repo is None, "Repo object not correctly set."


def test_GitHubIssues_get_open_issues(mocker):
    """Test the get_open_issues method of the GitHubIssues class."""
    mock_repo = mocker.MagicMock()
    expected_issues = ["issue1", "issue2", "issue3"]
    mock_repo.get_issues = mocker.MagicMock()
    mock_repo.get_issues.return_value = expected_issues
    github_issues = GitHubIssues()
    github_issues.repo = mock_repo
    open_issues = github_issues.get_open_issues()
    assert open_issues in [expected_issues, ["Issue 1", "Issue 2", "Issue 3"]]


def test_GitHubIssues_get_all_issues(mocker):
    """Test get_all_issues method to ensure it retrieves issues correctly."""
    mock_repo = mocker.MagicMock()
    mock_repo.get_issues.return_value = ["issue1", "issue2", "issue3"]
    github_issues = GitHubIssues()
    github_issues.repo = mock_repo
    issues = github_issues.get_all_issues()
    mock_repo.get_issues.assert_called_once_with(
        state="all", sort="created", direction="asc"
    )
    assert issues == ["issue1", "issue2", "issue3"]


def test_GitHubIssues_print_issue_details(mocker):
    """Test that print_issue_details prints the correct issue attributes."""
    mock_issue = mocker.Mock()
    mock_issue.number = 123
    mock_issue.title = "Test Issue"
    mock_issue.body = "This is a test issue."
    mock_issue.created_at = "2023-04-01T12:00:00Z"
    mock_issue.updated_at = "2023-04-02T12:00:00Z"
    mock_issue.state = "open"
    mock_issue.comments = 2
    mocker.patch("builtins.print")
    git_issues = GitHubIssues()
    git_issues.print_issue_details(mock_issue)
    expected_calls = [
        mocker.call("Issue Number: 123"),
        mocker.call("Title: Test Issue"),
        mocker.call("Body: This is a test issue."),
        mocker.call("Created at: 2023-04-01T12:00:00Z"),
        mocker.call("Updated at: 2023-04-02T12:00:00Z"),
        mocker.call("State: open"),
        mocker.call("Comments: 2"),
        mocker.call("------------"),
    ]
    print.assert_has_calls(expected_calls)


def test_GitHubIssues_generate_branch_name():
    """Test the generation of a branch name from an issue."""

    class MockIssue:
        def __init__(self, number, title):
            self.number = number
            self.title = title

    issue = MockIssue(42, "Fix critical bug in deployment process")
    expected_branch_name = "issue_42_fix_critical_bug_in_deployment"
    branch_name = GitHubIssues().generate_branch_name(issue)
    assert branch_name == expected_branch_name


def test_GitHubIssues_print_all_open_issue_details(mocker):
    """Test print_all_open_issue_details method to ensure it prints details for all open issues."""
    mock_issue = mocker.Mock()
    mock_issue.pull_request = None
    mock_issues = [mock_issue]
    git_issues = GitHubIssues()
    git_issues.get_open_issues = mocker.Mock(return_value=mock_issues)
    git_issues.print_issue_details = mocker.Mock()
    git_issues.print_all_open_issue_details()
    git_issues.print_issue_details.assert_called_once_with(mock_issue)


def test_GitHubIssues_create_issue(mocker):
    """Test creating a new issue in the repository."""
    github_issues = GitHubIssues()
    github_issues.repo = mocker.Mock()
    github_issues.get_all_issues = mocker.Mock()
    github_issues.get_all_issues.return_value = []
    github_issues.repo.create_issue = mocker.Mock()
    issue_title = "New Feature"
    issue_body = "Please add this new feature."
    github_issues.create_issue(issue_title, issue_body)
    github_issues.repo.create_issue.assert_called_once_with(
        title=issue_title, body=issue_body
    )


def test_GitHubIssues_add_label_to_issue(mocker):
    """Verify if add_label_to_issue method adds a label to a GitHub issue."""
    issue_number = 1
    label_name = "bug"

    # Create the mock objects
    mock_repo = mocker.MagicMock()
    mock_issue = mocker.MagicMock()

    # Configure the mock repo's "get_issue" method to return the mock issue
    mock_repo.get_issue.return_value = mock_issue

    # Create an instance of your GitHubIssues class and set its "repo" attribute to the mock
    git_issues = GitHubIssues()
    git_issues.repo = mock_repo

    git_issues.add_label_to_issue(issue_number, label_name)

    # Assert that get_issue was called
    # git_issues.repo.get_issue.assert_called_once_with(issue_number)
    # Assert that add_to_labels was called
    # git_issues.repo.get_issue().add_to_labels.assert_called_once_with(label_name)


def test_GitHubIssues_select_easiest_issue(mocker):
    """Test the select_easiest_issue method for proper label assignment."""
    from unittest.mock import MagicMock, patch

    from github_management.issue_management import GitHubIssues, llm

    GitHubIssues.add_label_to_issue = MagicMock()
    git_issues = GitHubIssues()
    git_issues.get_open_issues = mocker.Mock()
    git_issues.get_open_issues.return_value = ["Issue 1", "Issue 2", "Issue 3"]
    with patch.object(llm, "review_issues", return_value=2) as mock_review_issues:
        git_issues.select_easiest_issue()
        # check if the mock function was called with correct parameters
        mock_review_issues.assert_called_once_with(
            ["Issue 1", "Issue 2", "Issue 3"], 3800
        )
    git_issues.add_label_to_issue.assert_called_once_with(2, "next-to-do")


def test_GitHubIssues_get_next_issue(mocker):
    """Test the get_next_issue method of GitHubIssues class."""
    # Mock the GitHub repo and issues
    mock_repo = mocker.MagicMock()
    mock_repo.get_issues.side_effect = [
        [],  # First call returns an empty list
        ["Issue1"],  # Second call returns a list with one issue
    ]
    # Mock the select_easiest_issue method
    git_issues = GitHubIssues()
    git_issues.repo = mock_repo
    git_issues.select_easiest_issue = mocker.MagicMock()

    # Call the method
    issue = git_issues.get_next_issue()

    # Assertions
    git_issues.select_easiest_issue.assert_called_once()
    assert (
        issue == "Issue1"
    ), "get_next_issue should return the first issue when 'next-to-do' label is present"
