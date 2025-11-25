"""Tests for API route handlers."""

import json


async def test_hello(jp_fetch):
    """Test the hello endpoint."""
    response = await jp_fetch("jupyterlab-research-assistant-wwc-copilot", "hello")

    assert response.code == 200
    payload = json.loads(response.body)
    assert "data" in payload
    assert "Hello, world!" in payload["data"]


async def test_library_get_empty(jp_fetch):
    """Test getting library when empty."""
    response = await jp_fetch("jupyterlab-research-assistant-wwc-copilot", "library")

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert payload["data"] == []


async def test_library_post(jp_fetch):
    """Test adding a paper to the library."""
    paper_data = {
        "title": "Test Paper",
        "authors": ["Author 1", "Author 2"],
        "year": 2023,
        "abstract": "Test abstract"
    }

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper_data)
    )

    assert response.code == 201
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert payload["data"]["title"] == "Test Paper"
    assert payload["data"]["id"] is not None


async def test_library_post_no_data(jp_fetch):
    """Test POST library with no data."""
    from tornado.httpclient import HTTPClientError
    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "library",
            method="POST",
            body=json.dumps({})
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"


async def test_search_no_query(jp_fetch):
    """Test search endpoint without query parameter."""
    from tornado.httpclient import HTTPClientError
    try:
        response = await jp_fetch("jupyterlab-research-assistant-wwc-copilot", "search")
        # If no exception, check response
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "q" in payload["message"].lower()
    except HTTPClientError as e:
        # jp_fetch may raise for 4xx codes, check the response
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "q" in payload["message"].lower()


async def test_search_with_query(jp_fetch):
    """Test search endpoint with query."""
    # First add a paper
    paper_data = {
        "title": "Spaced Repetition Study",
        "authors": ["Researcher"],
        "abstract": "This paper studies spaced repetition",
        "year": 2023
    }
    await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper_data)
    )

    # Then search
    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "search",
        params={"q": "spaced"}
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert len(payload["data"]) >= 1


async def test_discovery_no_query(jp_fetch):
    """Test discovery endpoint without query parameter."""
    from tornado.httpclient import HTTPClientError
    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot", "discovery"
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"


async def test_discovery_with_query(jp_fetch):
    """Test discovery endpoint with query.

    May fail if API is down, but structure should work.
    """
    from tornado.httpclient import HTTPClientError
    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "discovery",
            params={"q": "machine learning", "limit": "5"}
        )
        # Should either succeed (200) or fail with API error (500), but not 400
        assert response.code in [200, 500]
        payload = json.loads(response.body)
        assert payload["status"] in ["success", "error"]
    except HTTPClientError as e:
        # If API fails, should be 500 or 599 (timeout), not 400
        assert e.code in [500, 599]
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"


async def test_import_no_file(jp_fetch):
    """Test import endpoint without file."""
    from tornado.httpclient import HTTPClientError
    from urllib.parse import urlencode
    try:
        body = urlencode({})
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "import",
            method="POST",
            body=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "file" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "file" in payload["message"].lower()
