"""Schema definitions for AI metadata extraction."""

LEARNING_SCIENCE_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "study_metadata": {
            "type": "object",
            "properties": {
                "methodology": {
                    "type": "string",
                    "enum": [
                        "RCT",
                        "Quasi-experimental",
                        "Observational",
                        "Case Study",
                        "Other",
                    ],
                    "description": "Research methodology",
                },
                "sample_size_baseline": {
                    "type": "integer",
                    "description": "Sample size at baseline",
                },
                "sample_size_endline": {
                    "type": "integer",
                    "description": "Sample size at endline",
                },
                "effect_sizes": {
                    "type": "object",
                    "description": "Reported effect sizes by outcome",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "d": {"type": "number", "description": "Cohen's d"},
                            "se": {"type": "number", "description": "Standard error"},
                        },
                    },
                },
            },
        },
        "learning_science_metadata": {
            "type": "object",
            "properties": {
                "learning_domain": {
                    "type": "string",
                    "enum": ["cognitive", "affective", "behavioral", "metacognitive"],
                    "description": "Primary learning domain",
                },
                "intervention_type": {
                    "type": "string",
                    "description": "Type of intervention (e.g., 'Spaced Repetition', 'Active Learning')",
                },
                "learning_objectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "What students were supposed to learn",
                },
                "intervention_components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific instructional techniques used",
                },
            },
        },
        "wwc_criteria": {
            "type": "object",
            "properties": {
                "baseline_n_treatment": {"type": "integer"},
                "baseline_n_control": {"type": "integer"},
                "endline_n_treatment": {"type": "integer"},
                "endline_n_control": {"type": "integer"},
                "randomization_method": {"type": "string"},
                "baseline_equivalence_reported": {"type": "boolean"},
            },
        },
    },
    "required": [],
}
