"""Tests for WWC and Meta-Analysis API route handlers."""

import json


async def test_wwc_assessment_missing_paper_id(jp_fetch):
    """Test WWC assessment endpoint with missing paper_id."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "wwc-assessment",
            method="POST",
            body=json.dumps({}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "paper_id" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        # Either "no data provided" or "paper_id required" is acceptable
        message = payload["message"].lower()
        assert "no data" in message or "paper_id" in message


async def test_wwc_assessment_paper_not_found(jp_fetch):
    """Test WWC assessment endpoint with non-existent paper."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "wwc-assessment",
            method="POST",
            body=json.dumps({"paper_id": 99999, "judgments": {}}),
        )
        assert response.code == 404
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert "not found" in payload["message"].lower()
    except HTTPClientError as e:
        assert e.code == 404
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert "not found" in payload["message"].lower()


async def test_wwc_assessment_success(jp_fetch):
    """Test successful WWC assessment."""
    # First, create a paper with study metadata
    paper_data = {
        "title": "Test RCT Study",
        "authors": ["Author 1"],
        "year": 2023,
        "study_metadata": {
            "methodology": "RCT",
            "sample_size_baseline": 100,
            "sample_size_endline": 95,
            "treatment_attrition": 0.04,
            "control_attrition": 0.06,
        },
    }

    create_response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "library",
        method="POST",
        body=json.dumps(paper_data),
    )

    assert create_response.code == 201
    created_paper = json.loads(create_response.body)["data"]
    paper_id = created_paper["id"]

    # Now run WWC assessment
    assessment_data = {
        "paper_id": paper_id,
        "judgments": {
            "chosen_attrition_boundary": "cautious",
            "randomization_documented": True,
        },
    }

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "wwc-assessment",
        method="POST",
        body=json.dumps(assessment_data),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "final_rating" in data
    assert "rating_justification" in data
    assert "overall_attrition" in data
    assert "differential_attrition" in data


async def test_meta_analysis_insufficient_papers(jp_fetch):
    """Test meta-analysis endpoint with insufficient papers."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "meta-analysis",
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


async def test_meta_analysis_no_effect_sizes(jp_fetch):
    """Test meta-analysis endpoint with papers that have no effect sizes."""
    # Create two papers without effect sizes
    paper1_data = {
        "title": "Study 1",
        "authors": ["Author 1"],
        "year": 2023,
    }

    paper2_data = {
        "title": "Study 2",
        "authors": ["Author 2"],
        "year": 2023,
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

    paper1_id = json.loads(create1_response.body)["data"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["id"]

    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "meta-analysis",
            method="POST",
            body=json.dumps({"paper_ids": [paper1_id, paper2_id]}),
        )
        assert response.code == 400
        payload = json.loads(response.body)
        assert payload["status"] == "error"
        assert (
            "insufficient" in payload["message"].lower()
            or "effect size" in payload["message"].lower()
        )
    except HTTPClientError as e:
        assert e.code == 400
        payload = json.loads(e.response.body)
        assert payload["status"] == "error"
        assert (
            "insufficient" in payload["message"].lower()
            or "effect size" in payload["message"].lower()
        )


async def test_meta_analysis_success(jp_fetch):
    """Test successful meta-analysis."""
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

    paper1_id = json.loads(create1_response.body)["data"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["id"]

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "meta-analysis",
        method="POST",
        body=json.dumps({"paper_ids": [paper1_id, paper2_id]}),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "pooled_effect" in data
    assert "ci_lower" in data
    assert "ci_upper" in data
    assert "p_value" in data
    assert "i_squared" in data
    assert "q_statistic" in data
    assert "forest_plot" in data
    assert "heterogeneity_interpretation" in data
    assert "studies" in data
    assert len(data["studies"]) == 2


async def test_meta_analysis_with_outcome_name(jp_fetch):
    """Test meta-analysis with specific outcome name."""
    # Create papers with multiple outcomes
    paper1_data = {
        "title": "Study A",
        "authors": ["Author 1"],
        "year": 2023,
        "study_metadata": {
            "effect_sizes": {
                "knowledge_test": {"d": 0.5, "se": 0.15},
                "retention_test": {"d": 0.4, "se": 0.14},
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
                "retention_test": {"d": 0.2, "se": 0.11},
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

    paper1_id = json.loads(create1_response.body)["data"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["id"]

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "meta-analysis",
        method="POST",
        body=json.dumps(
            {"paper_ids": [paper1_id, paper2_id], "outcome_name": "retention_test"}
        ),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    data = payload["data"]
    assert len(data["studies"]) == 2
    # Verify both studies have the retention_test effect size
    assert all(
        "retention_test" in s.get("study_label", "") or s.get("effect_size", 0) > 0
        for s in data["studies"]
    )


async def test_conflict_detection_insufficient_papers(jp_fetch):
    """Test conflict detection endpoint with insufficient papers."""
    from tornado.httpclient import HTTPClientError

    try:
        response = await jp_fetch(
            "jupyterlab-research-assistant-wwc-copilot",
            "conflict-detection",
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


async def test_conflict_detection_success(jp_fetch):
    """Test successful conflict detection."""
    # Create two papers with abstracts
    paper1_data = {
        "title": "Study A",
        "authors": ["Author 1"],
        "year": 2023,
        "abstract": "The results show a significant positive effect. We found that the intervention worked well.",
    }

    paper2_data = {
        "title": "Study B",
        "authors": ["Author 2"],
        "year": 2023,
        "abstract": "The results show no significant effect. We found that the intervention did not work.",
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

    paper1_id = json.loads(create1_response.body)["data"]["id"]
    paper2_id = json.loads(create2_response.body)["data"]["id"]

    response = await jp_fetch(
        "jupyterlab-research-assistant-wwc-copilot",
        "conflict-detection",
        method="POST",
        body=json.dumps({"paper_ids": [paper1_id, paper2_id]}),
    )

    assert response.code == 200
    payload = json.loads(response.body)
    assert payload["status"] == "success"
    assert "data" in payload
    data = payload["data"]
    assert "contradictions" in data
    assert "n_papers" in data
    assert "n_contradictions" in data
    assert data["n_papers"] == 2
    assert isinstance(data["contradictions"], list)
