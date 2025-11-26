"""
Conflict detection using Natural Language Inference (NLI) models.

IMPORTANT FOR DEVELOPERS:
- This module uses cross-encoder NLI models (e.g., DeBERTa) to detect contradictions
- We use direct tokenizer/model access instead of pipeline() for better control over
  tokenization parameters (padding, truncation) which is critical for avoiding tensor errors
- Cross-encoder models require (premise, hypothesis) tuple format - NOT string concatenation
- Always ensure padding=True and truncation=True to handle variable-length inputs
- Device handling (CPU/GPU) is automatic but can be customized if needed
- Label mappings vary by model - always check model.config for correct label IDs
"""

import logging
import re

logger = logging.getLogger(__name__)

# Optional: Only import if transformers is available
# NOTE: transformers is a heavy dependency - the extension should work without it
# but conflict detection will be disabled if not available
try:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
    )

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
        self.nli_pipeline = None  # DEPRECATED: kept for backwards compatibility
        self.tokenizer = None  # AutoTokenizer instance - required for tokenization
        self.model = None  # AutoModelForSequenceClassification instance - the NLI model
        self.ai_extractor = ai_extractor

        if TRANSFORMERS_AVAILABLE:
            try:
                # CRITICAL: Load tokenizer and model directly (not via pipeline)
                # This gives us control over padding/truncation which prevents tensor errors
                # Pipeline() can fail with "expected sequence of length X at dim 1 (got Y)"
                # when batching variable-length inputs without explicit padding
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    model_name
                )
                # Set to evaluation mode (disables dropout, batch norm updates, etc.)
                # This is important for consistent inference results
                self.model.eval()

                # Device handling: automatically use GPU if available, otherwise CPU
                # NOTE: First model load is slow (downloading weights), subsequent uses are fast
                # Consider caching models if loading multiple times
                device = -1  # CPU
                if torch.cuda.is_available():
                    device = 0  # GPU if available
                if device >= 0:
                    self.model = self.model.to(f"cuda:{device}")
                logger.info(f"Loaded NLI model: {model_name}")
            except Exception:
                # Graceful degradation: if model loading fails, disable conflict detection
                # but don't crash the extension
                logger.exception("Failed to load NLI model")
                self.tokenizer = None
                self.model = None
        else:
            logger.warning("transformers not available. Conflict detection disabled.")

    def _are_same_topic(self, finding1: str, finding2: str) -> bool:
        """
        Check if two findings are about the same topic/intervention/outcome.

        IMPORTANT: This is a heuristic filter to reduce false positives.
        The NLI model can flag contradictions between findings about completely
        different research questions (e.g., "tutoring improves math" vs "curriculum
        improves reading"). This function filters those out before expensive NLI inference.

        LIMITATIONS:
        - Uses simple keyword matching - may miss semantic similarity
        - May filter out valid comparisons if keywords don't overlap
        - Consider improving with semantic similarity (embeddings) for better accuracy

        Args:
            finding1: First finding statement
            finding2: Second finding statement

        Returns:
            True if findings appear to be about the same topic
        """
        # Extract key terms (simple keyword-based approach)
        finding1_lower = finding1.lower()
        finding2_lower = finding2.lower()

        # Common intervention keywords
        intervention_keywords = [
            "tutoring",
            "instruction",
            "intervention",
            "treatment",
            "program",
            "curriculum",
            "method",
            "approach",
            "strategy",
            "technique",
        ]

        # Common outcome keywords
        outcome_keywords = [
            "reading",
            "math",
            "comprehension",
            "knowledge",
            "performance",
            "achievement",
            "score",
            "test",
            "learning",
            "skill",
        ]

        # Check if findings share intervention or outcome keywords
        f1_interventions = [kw for kw in intervention_keywords if kw in finding1_lower]
        f2_interventions = [kw for kw in intervention_keywords if kw in finding2_lower]
        f1_outcomes = [kw for kw in outcome_keywords if kw in finding1_lower]
        f2_outcomes = [kw for kw in outcome_keywords if kw in finding2_lower]

        # If both mention interventions, check for overlap
        if (
            f1_interventions
            and f2_interventions
            and not set(f1_interventions).intersection(set(f2_interventions))
        ):
            # Different interventions - likely different topics
            return False

        # If both mention outcomes, check for overlap
        if (
            f1_outcomes
            and f2_outcomes
            and not set(f1_outcomes).intersection(set(f2_outcomes))
        ):
            # Different outcomes - likely different topics
            return False

        # If one has intervention/outcome keywords and the other doesn't, be cautious
        # but don't filter out (might be about same topic with different wording)
        # Return True if findings might be on the same topic (no clear separation)
        return not (
            (
                f1_interventions
                and f2_interventions
                and not set(f1_interventions).intersection(set(f2_interventions))
            )
            or (
                f1_outcomes
                and f2_outcomes
                and not set(f1_outcomes).intersection(set(f2_outcomes))
            )
        )

    def find_contradictions(
        self,
        findings1: list[str],
        findings2: list[str],
        confidence_threshold: float = 0.8,
        filter_different_topics: bool = True,
    ) -> list[dict]:
        """
        Compare two lists of findings and identify contradictions.

        Args:
            findings1: List of finding statements from first study
            findings2: List of finding statements from second study
            confidence_threshold: Minimum confidence score for contradiction
                (0.0 to 1.0)
            filter_different_topics: If True, filter out comparisons between
                findings about different topics/interventions/outcomes

        Returns:
            List of contradiction dictionaries with:
                - finding1: First finding statement
                - finding2: Second finding statement
                - confidence: Confidence score (0.0 to 1.0)
                - label: NLI label (contradiction/entailment/neutral)
        """
        if self.tokenizer is None or self.model is None:
            logger.warning("NLI model not available. Returning empty results.")
            return []

        contradictions = []

        for f1 in findings1:
            for f2 in findings2:
                try:
                    # Filter out comparisons between different topics if enabled
                    # This reduces false positives and improves performance
                    if filter_different_topics and not self._are_same_topic(f1, f2):
                        continue

                    # CRITICAL: Tokenize the pair with proper formatting for cross-encoder
                    # Cross-encoder models expect (premise, hypothesis) tuple format
                    # DO NOT concatenate strings - use tokenizer(f1, f2) format
                    #
                    # REQUIRED parameters to prevent tensor errors:
                    # - padding=True: Ensures all sequences in batch have same length
                    # - truncation=True: Cuts sequences longer than max_length
                    # - max_length=512: Standard BERT/DeBERTa limit (model-dependent)
                    #
                    # Without these, you'll get: "ValueError: expected sequence of length X at dim 1 (got Y)"
                    inputs = self.tokenizer(
                        f1,  # premise (first finding)
                        f2,  # hypothesis (second finding)
                        return_tensors="pt",  # Return PyTorch tensors
                        padding=True,  # REQUIRED: pad to same length
                        truncation=True,  # REQUIRED: truncate if too long
                        max_length=512,  # Model's maximum sequence length
                    )

                    # CRITICAL: Move inputs to same device as model (CPU or GPU)
                    # Inputs and model must be on the same device or PyTorch will error
                    # This handles both CPU-only and GPU-accelerated inference
                    device = next(self.model.parameters()).device
                    inputs = {k: v.to(device) for k, v in inputs.items()}

                    # Get model predictions
                    # torch.no_grad() disables gradient computation (faster, less memory)
                    # This is required for inference - we don't need gradients
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        # Apply softmax to convert logits to probabilities
                        # dim=-1 means apply along the last dimension (class probabilities)
                        predictions = torch.nn.functional.softmax(
                            outputs.logits, dim=-1
                        )

                    # CRITICAL: Label mapping varies by model - always check config
                    # Different models use different label IDs:
                    # - Some models: 0=contradiction, 1=entailment, 2=neutral
                    # - Other models: 0=entailment, 1=neutral, 2=contradiction
                    # - Always use model.config to get correct mapping
                    #
                    # NOTE: id2label maps class_id -> label_name (e.g., 0 -> "contradiction")
                    #       label2id maps label_name -> class_id (e.g., "contradiction" -> 0)
                    if (
                        hasattr(self.model.config, "id2label")
                        and self.model.config.id2label
                    ):
                        id2label = self.model.config.id2label
                    elif (
                        hasattr(self.model.config, "label2id")
                        and self.model.config.label2id
                    ):
                        # Reverse label2id to get id2label
                        id2label = {v: k for k, v in self.model.config.label2id.items()}
                    else:
                        # Fallback: Default mapping for MNLI models
                        # WARNING: This may be wrong for some models - check model card!
                        id2label = {
                            0: "contradiction",
                            1: "entailment",
                            2: "neutral",
                        }

                    # Extract probability scores for all labels
                    # Move to CPU and convert to numpy for easier manipulation
                    probs = predictions[0].cpu().numpy()
                    label_scores = {}
                    for class_id, prob in enumerate(probs):
                        # Get label name from mapping, default to "label_{id}" if unknown
                        label_name = id2label.get(class_id, f"label_{class_id}").lower()
                        label_scores[label_name] = float(prob)

                    # Get contradiction score specifically
                    # This is the probability that the two findings contradict each other
                    # We use this (not the predicted class) because we want the confidence
                    # in contradiction, not just whether it's the top prediction
                    contradiction_score = label_scores.get("contradiction", 0.0)

                    # Also get the predicted label for reporting
                    predicted_class_id = predictions.argmax().item()
                    predicted_label = id2label.get(
                        predicted_class_id, "unknown"
                    ).lower()

                    # Check if contradiction confidence meets threshold
                    # confidence_threshold is typically 0.7-0.9 to balance precision/recall
                    # Lower threshold = more contradictions detected (but more false positives)
                    # Higher threshold = fewer contradictions (but may miss some)
                    if contradiction_score >= confidence_threshold:
                        contradictions.append(
                            {
                                "finding1": f1,
                                "finding2": f2,
                                "confidence": float(contradiction_score),
                                "label": predicted_label,
                            }
                        )
                except Exception:
                    # CRITICAL: Catch all exceptions to prevent one bad finding pair
                    # from crashing the entire conflict detection process
                    # Log the error but continue processing other pairs
                    # Common errors: tokenization failures, model inference errors,
                    # device mismatches, out-of-memory errors
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
        # NOTE: This is a simple heuristic - AI extraction is preferred when available
        # This method prioritizes specific, testable claims over generic descriptions
        #
        # PERFORMANCE: This is O(n) where n = number of sentences
        # For very long papers, consider chunking or limiting sentence count
        findings = []

        # High-priority keywords: indicate specific findings or results
        # These phrases typically signal actual research findings, not just descriptions
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
            # Scoring weights are tuned heuristically - may need adjustment based on
            # evaluation against ground truth findings from papers
            if has_high_priority:
                score += 3  # High weight for phrases like "found that", "results show"
            if has_medium_priority:
                score += (
                    1  # Lower weight for generic terms like "significant", "effect"
                )
            if has_number or has_percent:
                score += 2  # Quantitative findings are more specific and testable
            if has_effect_size:
                score += 3  # Effect sizes are highly specific and important for meta-analysis
            if len(sentence) > 50:
                score += 1  # Longer sentences often contain more detail and context

            if score > 0:
                scored_sentences.append((score, sentence))

        # Sort by score (highest first) and take top findings
        # This ensures we return the most specific, quantitative findings first
        # which are most useful for conflict detection
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        findings = [sentence for _, sentence in scored_sentences[:max_findings]]

        return findings
