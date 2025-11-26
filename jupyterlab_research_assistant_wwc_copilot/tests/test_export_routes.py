"""Tests for Export API route handlers."""

import json


async def test_meta_analysis_export_insufficient_papers(jp_fetch):
    """Test meta-analysis export endpoint with insufficient papers."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "meta-analysis/export",
            method="POST",
            body=json.dumps({"paper_ids": [1]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "at least 2" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "at least 2" in payload["message"].lower()


async def test_meta_analysis_export_success(jp_fetch):
    """Test successful meta-analysis CSV export."""
    # Create two papers with effect sizes
    paper1_data = {
        "title": "Study A",
        "authors": ["Author 1"],
        "year": 2023,
        "study_metadata": {
            "effect_sizes": {
                "knowledge_test": {"d": 0.5, "se": 0.15},
            },
        },
    }

    paper2_data = {
        "title": "Study B",
        "authors": ["Author 2"],
        "year": 2023,
        "study_metadata": {
            "effect_sizes": {
                "knowledge_test": {"d": 0.3, "se": 0.12},
            },
        },
    }

    create1_response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper1_data),
    )

    create2_response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper2_data),
    )

    paper1_id = json.loads(create1_response.body)["data"]["paper"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["paper"]["id"]

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "meta-analysis/export",
        method="POST",
        body=json.dumps({"paper_ids": [paper1_id, paper2_id]}),
    )

    assert response.code == 200
    # Note: Jupyter Server may override Content-Type header, but content should be CSV
    csv_content = response.body.decode("utf-8")
    assert "Study" in csv_content
    assert "Effect Size" in csv_content
    assert "Pooled Effect" in csv_content
    # Verify it's actually CSV format (comma-separated)
    assert "," in csv_content


async def test_synthesis_export_insufficient_papers(jp_fetch):
    """Test synthesis export endpoint with insufficient papers."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "synthesis/export",
            method="POST",
            body=json.dumps({"paper_ids": [1]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "at least 2" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "at least 2" in payload["message"].lower()


async def test_synthesis_export_success(jp_fetch):
    """Test successful synthesis Markdown export."""
    # Create two papers
    paper1_data = {
        "title": "Study A",
        "authors": ["Author 1"],
        "year": 2023,
        "abstract": "Results show significant effect.",
        "study_metadata": {
            "effect_sizes": {
                "knowledge_test": {"d": 0.5, "se": 0.15},
            },
        },
    }

    paper2_data = {
        "title": "Study B",
        "authors": ["Author 2"],
        "year": 2023,
        "abstract": "Results show no effect.",
        "study_metadata": {
            "effect_sizes": {
                "knowledge_test": {"d": 0.3, "se": 0.12},
            },
        },
    }

    create1_response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper1_data),
    )

    create2_response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper2_data),
    )

    paper1_id = json.loads(create1_response.body)["data"]["paper"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["paper"]["id"]

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "synthesis/export",
        method="POST",
        body=json.dumps(
            {
                "paper_ids": [paper1_id, paper2_id],
                "include_meta_analysis": True,
                "include_conflicts": True,
            }
        ),
    )

    assert response.code == 200
    # Note: Jupyter Server may override Content-Type header, but content should be Markdown
    markdown_content = response.body.decode("utf-8")
    assert "# Synthesis Report" in markdown_content
    assert "Meta-Analysis" in markdown_content
    assert "References" in markdown_content
    # Verify it's actually Markdown format
    assert "##" in markdown_content or "###" in markdown_content
