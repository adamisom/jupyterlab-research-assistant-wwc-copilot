"""
AI-powered metadata extraction from PDF text.

IMPORTANT FOR DEVELOPERS:
- Supports Ollama (local) and OpenAI/Claude (cloud) providers
- Text is truncated to 16KB to fit context windows (adjust if using larger models)
- JSON parsing is lenient - attempts to extract JSON from malformed responses
- Always set timeouts for API calls to prevent hanging requests
"""

import json
import logging
import re
from typing import Any, Optional

import requests

from .extraction_schema import LEARNING_SCIENCE_EXTRACTION_SCHEMA

logger = logging.getLogger(__name__)


class AIExtractor:
    """Extract metadata from PDF text using AI."""

    def __init__(
        self,
        provider: str = "ollama",
        api_key: Optional[str] = None,
        model: str = "llama3",
        ollama_url: str = "http://localhost:11434",
    ):
        self.provider = provider
        self.model = model
        self.ollama_url = ollama_url

        if provider in ["claude", "openai"]:
            if not api_key:
                raise ValueError(f"API key required for {provider}")
            try:
                from openai import OpenAI  # noqa: PLC0415

                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.anthropic.com/v1"
                    if provider == "claude"
                    else None,
                )
            except ImportError as e:
                raise ImportError(
                    "openai package required for Claude/OpenAI. Install with: pip install openai"
                ) from e
        else:
            self.client = None

    def extract_metadata(
        self, text: str, schema: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Extract metadata from text using AI.

        Args:
            text: PDF text to extract from
            schema: JSON schema for extraction (defaults to learning science schema)

        Returns:
            Extracted metadata dictionary
        """
        if schema is None:
            schema = LEARNING_SCIENCE_EXTRACTION_SCHEMA

        # CRITICAL: Truncate text to fit in context window
        # Most models have 4K-32K token limits - 16K chars is conservative
        # Adjust max_chars if using models with larger context windows
        max_chars = 16000
        truncated_text = text[:max_chars] if len(text) > max_chars else text

        prompt = f"""Extract the following information from this academic paper.
Respond with a single, valid JSON object that conforms to the provided schema.

Schema:
{json.dumps(schema, indent=2)}

Paper Text:
{truncated_text}

Return only valid JSON, no additional text."""

        try:
            if self.provider == "ollama":
                return self._extract_with_ollama(prompt)
            else:
                return self._extract_with_openai(prompt)
        except Exception:
            logger.exception("AI extraction failed")
            return {}

    def _extract_with_ollama(self, prompt: str) -> dict[str, Any]:
        """Extract using Ollama API."""
        # CRITICAL: Set timeout to prevent hanging requests
        # Large models can take 60-120 seconds for complex extractions
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Request JSON format (not all models support this)
            },
            timeout=120,  # 2 minute timeout for large models
        )
        response.raise_for_status()
        result = response.json()
        extracted_text = result.get("response", "")

        # Parse JSON from response
        # NOTE: Some models return JSON wrapped in markdown or extra text
        # Fallback regex extraction handles malformed responses gracefully
        try:
            return json.loads(extracted_text)
        except json.JSONDecodeError:
            logger.warning(
                "Ollama returned invalid JSON, attempting to extract JSON from response"
            )
            # Fallback: Extract JSON object from text (handles markdown code blocks, etc.)
            json_match = re.search(r"\{.*\}", extracted_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}

    def _extract_with_openai(self, prompt: str) -> dict[str, Any]:
        """Extract using OpenAI/Anthropic API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
