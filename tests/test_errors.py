import json


def test_invalid_path_renders_custom_404(client):
    """
    Test mandatory requirement:
    Test an invalid path such as /this-page-does-not-exist and ensure that it displays
    the custom 404 page rather than the default Flask error screen.
    """
    response = client.get('/this-page-does-not-exist')
    assert response.status_code == 404
    html = response.get_data(as_text=True)

    # MysteryMart branding
    assert 'MysteryMart' in html
    # Helpful error message
    assert "We Couldn't Find That Mystery Box" in html or '404' in html
    # Button to return home
    assert 'Return Home' in html or 'href="/"' in html
    # "Ask the Assistant" button
    assert 'Ask the Assistant' in html or 'askAssistant' in html
    # Chat widget present
    assert 'mmChatLauncher' in html


def test_custom_500_handler(app):
    """
    Test mandatory requirement:
    Controlled test of custom 500 internal server error handler.
    Must show safe message without exposing stack traces or database credentials.
    """
    app.testing = False
    client = app.test_client()
    try:
        response = client.get('/test-500')
        assert response.status_code == 500
        html = response.get_data(as_text=True)

        # Branding & friendly message
        assert 'MysteryMart' in html
        assert 'Something Went Unexpected' in html or '500' in html
        assert 'Return Home' in html
        assert 'Ask the Assistant' in html
        # Verify no raw python traceback is leaked to user
        assert 'Traceback (most recent call last)' not in html
        assert 'Controlled test exception' not in html
    finally:
        app.testing = True


def test_custom_460_handler(client):
    """
    Test custom application status code 460:
    MysteryMart Unboxing Concurrency / Stock Allocation Conflict.
    """
    response = client.get('/test-460')
    assert response.status_code == 460
    html = response.get_data(as_text=True)
    assert '460' in html
    assert 'MysteryMart Custom Code' in html or 'application-specific status code' in html
    assert 'Return Home' in html
    assert 'Ask the Assistant' in html


def test_json_error_responses(client):
    """Verify API endpoints return structured JSON errors."""
    response = client.get(
        '/api/non-existent-api-endpoint',
        headers={'Accept': 'application/json'}
    )
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == 'Not Found'
    assert data['status_code'] == 404
