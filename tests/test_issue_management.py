

def test_slugify():
    from github_management.issue_management import slugify

    # Test with alphanumeric characters
    title = 'Test Title 1'
    expected_slug = 'Test_Title_1'
    assert slugify(title) == expected_slug

    # Test with non-alphanumeric characters
    title = 'Test Title $&@!'
    expected_slug = 'Test_Title_'
    assert slugify(title) == expected_slug

    # Test with max_length
    title = 'This is a very long title that should be truncated'
    expected_slug = 'This_is_a_very_long_title_tha'
    assert slugify(title) == expected_slug

