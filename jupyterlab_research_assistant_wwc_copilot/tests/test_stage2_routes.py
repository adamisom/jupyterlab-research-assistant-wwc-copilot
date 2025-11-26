"""Tests for Stage 2 enhancement API route handlers."""

import json


async def test_subgroup_analysis_missing_variable(jp_fetch):
    """Test subgroup analysis endpoint with missing subgroup_variable."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "subgroup-analysis",
            method="POST",
            body=json.dumps({"paper_ids": [1, 2]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "subgroup_variable" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "subgroup_variable" in payload["message"].lower()


async def test_subgroup_analysis_insufficient_papers(jp_fetch):
    """Test subgroup analysis endpoint with insufficient papers."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "subgroup-analysis",
            method="POST",
            body=json.dumps({"paper_ids": [1], "subgroup_variable": "age_group"}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"


async def test_bias_assessment_insufficient_studies(jp_fetch):
    """Test bias assessment endpoint with insufficient studies."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "bias-assessment",
            method="POST",
            body=json.dumps({"paper_ids": [1, 2]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "at least 3" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "at least 3" in payload["message"].lower()


async def test_sensitivity_analysis_insufficient_studies(jp_fetch):
    """Test sensitivity analysis endpoint with insufficient studies."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "sensitivity-analysis",
            method="POST",
            body=json.dumps({"paper_ids": [1, 2]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "at least 3" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "at least 3" in payload["message"].lower()


async def test_subgroup_analysis_with_papers(jp_fetch):
    """Test subgroup analysis with valid papers."""
    # First add papers with effect sizes and subgroup data
    paper1 = {
        "title": "Study A",
        "authors": ["Author 1"],
        "year": 2023,
        "study_metadata": {"effect_sizes": {"outcome1": {"d": 0.5, "se": 0.15}}},
        "learning_science_metadata": {"age_group": "young"},
    }

    paper2 = {
        "title": "Study B",
        "authors": ["Author 2"],
        "year": 2023,
        "study_metadata": {"effect_sizes": {"outcome1": {"d": 0.3, "se": 0.12}}},
        "learning_science_metadata": {"age_group": "young"},
    }

    # Add papers
    response1 = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper1),
    )
    paper1_id = json.loads(response1.body)["data"]["paper"]["id"]

    response2 = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper2),
    )
    paper2_id = json.loads(response2.body)["data"]["paper"]["id"]

    # Perform subgroup analysis
    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "subgroup-analysis",
        method="POST",
        body=json.dumps(
            {
                "paper_ids": [paper1_id, paper2_id],
                "subgroup_variable": "age_group",
                "outcome_name": "outcome1",
            }
        ),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "subgroups" in data
    assert "overall" in data
    assert "subgroup_variable" in data
    assert data["subgroup_variable"] == "age_group"


async def test_bias_assessment_with_papers(jp_fetch):
    """Test bias assessment with valid papers."""
    import warnings

    # Add papers with effect sizes
    papers = []
    for i in range(3):
        paper = {
            "title": f"Study {i + 1}",
            "authors": [f"Author {i + 1}"],
            "year": 2023,
            "study_metadata": {
                "effect_sizes": {"outcome1": {"d": 0.5 + i * 0.1, "se": 0.15}}
            },
        }
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "library",
            method="POST",
            body=json.dumps(paper),
        )
        papers.append(json.loads(response.body)["data"]["paper"]["id"])

    # Perform bias assessment - suppress expected numerical warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        warnings.filterwarnings("ignore", message=".*ill-conditioned.*")
        warnings.filterwarnings("ignore", message=".*Ill-conditioned.*")
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "bias-assessment",
            method="POST",
            body=json.dumps({"paper_ids": papers, "outcome_name": "outcome1"}),
        )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "eggers_test" in data
    assert "funnel_plot" in data
    assert "n_studies" in data
    assert data["n_studies"] == 3
    assert data["eggers_test"]["interpretation"] is not None


async def test_sensitivity_analysis_with_papers(jp_fetch):
    """Test sensitivity analysis with valid papers."""
    # Add papers with effect sizes
    papers = []
    for i in range(3):
        paper = {
            "title": f"Study {i + 1}",
            "authors": [f"Author {i + 1}"],
            "year": 2023,
            "study_metadata": {
                "effect_sizes": {"outcome1": {"d": 0.5 + i * 0.1, "se": 0.15}}
            },
        }
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "library",
            method="POST",
            body=json.dumps(paper),
        )
        papers.append(json.loads(response.body)["data"]["paper"]["id"])

    # Perform sensitivity analysis
    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "sensitivity-analysis",
        method="POST",
        body=json.dumps({"paper_ids": papers, "outcome_name": "outcome1"}),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "overall_effect" in data
    assert "leave_one_out" in data
    assert "influence_diagnostics" in data
    assert "n_studies" in data
    assert data["n_studies"] == 3
    assert len(data["leave_one_out"]) == 3
    assert len(data["influence_diagnostics"]) == 3
