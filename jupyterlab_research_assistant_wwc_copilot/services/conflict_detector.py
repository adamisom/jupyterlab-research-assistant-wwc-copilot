"""Conflict detection using Natural Language Inference (NLI) models."""

import logging
import re

logger = logging.getLogger(__name__)

# Optional: Only import if transformers is available
try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning(
        "transformers library not available. Conflict detection will be disabled."
    )


class ConflictDetector:
    """
    Detects contradictions between study findings using NLI models.

    Uses a pre-trained NLI model (e.g., DeBERTa fine-tuned on MNLI)
    to identify contradictory findings across papers.
    """

    def __init__(
        self, model_name: str = "cross-encoder/nli-deberta-v3-base", ai_extractor=None
    ):
        """
        Initialize NLI pipeline.

        Args:
            model_name: Hugging Face model identifier for NLI model
            ai_extractor: Optional AI extractor service for finding extraction
        """
        self.model_name = model_name
        self.nli_pipeline = None
        self.ai_extractor = ai_extractor

        if TRANSFORMERS_AVAILABLE:
            try:
                self.nli_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    device=-1,  # Use CPU (-1), set to 0 for GPU if available
                )
                logger.info(f"Loaded NLI model: {model_name}")
            except Exception:
                logger.exception("Failed to load NLI model")
                self.nli_pipeline = None
        else:
            logger.warning("transformers not available. Conflict detection disabled.")

    def find_contradictions(
        self,
        findings1: list[str],
        findings2: list[str],
        confidence_threshold: float = 0.8,
    ) -> list[dict]:
        """
        Compare two lists of findings and identify contradictions.

        Args:
            findings1: List of finding statements from first study
            findings2: List of finding statements from second study
            confidence_threshold: Minimum confidence score for contradiction
                (0.0 to 1.0)

        Returns:
            List of contradiction dictionaries with:
                - finding1: First finding statement
                - finding2: Second finding statement
                - confidence: Confidence score (0.0 to 1.0)
                - label: NLI label (contradiction/entailment/neutral)
        """
        if self.nli_pipeline is None:
            logger.warning("NLI pipeline not available. Returning empty results.")
            return []

        contradictions = []

        for f1 in findings1:
            for f2 in findings2:
                try:
                    # Format for NLI: premise [SEP] hypothesis
                    result = self.nli_pipeline(f"{f1} [SEP] {f2}")

                    # Handle different return formats
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]

                    label = result.get("label", "").lower()
                    score = result.get("score", 0.0)

                    # Check for contradiction
                    if "contradict" in label and score >= confidence_threshold:
                        contradictions.append(
                            {
                                "finding1": f1,
                                "finding2": f2,
                                "confidence": float(score),
                                "label": label,
                            }
                        )
                except Exception:
                    logger.exception("Error processing findings")
                    continue

        return contradictions

    def extract_key_findings(
        self, paper_text: str, max_findings: int = 5, use_ai: bool = True
    ) -> list[str]:
        """
        Extract key findings from paper text using AI extraction.

        Args:
            paper_text: Full text of the paper
            max_findings: Maximum number of findings to extract
            use_ai: Whether to use AI extraction (if available)

        Returns:
            List of finding statements
        """
        if not paper_text:
            return []

        # Use AI extraction if available
        if use_ai and self.ai_extractor:
            schema = {
                "type": "object",
                "properties": {
                    "key_findings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "List of key findings or conclusions from the study"
                        ),
                    }
                },
                "required": ["key_findings"],
            }

            try:
                result = self.ai_extractor.extract_metadata(paper_text, schema)
                findings = result.get("key_findings", [])
                return findings[:max_findings]
            except Exception as e:
                logger.warning(
                    f"AI extraction failed, falling back to keyword method: {e!s}"
                )

        # Fallback to keyword-based extraction
        # Prioritize specific, testable claims over generic descriptions
        findings = []

        # High-priority keywords: indicate specific findings or results
        high_priority_keywords = [
            "found that",
            "results show",
            "demonstrated",
            "revealed",
            "increased by",
            "decreased by",
            "improved",
            "reduced",
            "effect size",
            "cohen's d",
            "significant effect",
            "no significant",
        ]

        # Medium-priority keywords: indicate conclusions or evidence
        medium_priority_keywords = [
            "significant",
            "conclusion",
            "indicate",
            "suggest",
            "evidence",
            "effect",
            "impact",
        ]

        # Low-priority: generic descriptive phrases (avoid if possible)
        low_priority_phrases = [
            "this study examined",
            "this study investigated",
            "the purpose of",
            "the study aimed",
        ]

        sentences = paper_text.split(".")
        scored_sentences = []

        for sentence_raw in sentences:
            sentence = sentence_raw.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue

            sentence_lower = sentence.lower()

            # Skip sentences that are just describing what was studied
            if any(phrase in sentence_lower for phrase in low_priority_phrases):
                continue

            # Score sentences based on specificity
            score = 0
            has_high_priority = any(
                kw in sentence_lower for kw in high_priority_keywords
            )
            has_medium_priority = any(
                kw in sentence_lower for kw in medium_priority_keywords
            )

            # Check for quantitative indicators (numbers, percentages, effect sizes)
            has_number = bool(re.search(r"\d+", sentence))
            has_percent = "%" in sentence or "percent" in sentence_lower
            has_effect_size = any(
                term in sentence_lower
                for term in ["d =", "d=", "g =", "g=", "effect size", "cohen"]
            )

            # Scoring: prioritize specific, quantitative findings
            if has_high_priority:
                score += 3
            if has_medium_priority:
                score += 1
            if has_number or has_percent:
                score += 2  # Quantitative findings are more specific
            if has_effect_size:
                score += 3  # Effect sizes are highly specific
            if len(sentence) > 50:
                score += 1  # Longer sentences often contain more detail

            if score > 0:
                scored_sentences.append((score, sentence))

        # Sort by score (highest first) and take top findings
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        findings = [sentence for _, sentence in scored_sentences[:max_findings]]

        return findings
