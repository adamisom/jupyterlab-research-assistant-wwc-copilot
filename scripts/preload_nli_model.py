"""
Pre-load the NLI model for conflict detection.

This script downloads and caches the NLI model so it's ready for immediate use.
It's idempotent - if the model is already cached, it just loads from cache (fast).

Usage:
    python scripts/preload_nli_model.py

Or import and call:
    from scripts.preload_nli_model import preload_nli_model
    preload_nli_model()
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


def preload_nli_model(model_name: str = "cross-encoder/nli-deberta-v3-base") -> bool:
    """
    Pre-load the NLI model for conflict detection.

    This function is idempotent - if the model is already cached,
    it will load from cache quickly without re-downloading.

    Args:
        model_name: Hugging Face model identifier

    Returns:
        True if model was loaded successfully, False otherwise
    """
    try:
        from transformers import (  # noqa: PLC0415
            AutoModelForSequenceClassification,
            AutoTokenizer,
        )
    except ImportError:
        logger.warning(
            "transformers library not available. "
            "Install with: pip install 'jupyterlab-research-assistant-wwc-copilot[conflict-detection]'"
        )
        return False

    try:
        logger.info(f"Loading NLI model: {model_name}")
        logger.info(
            "Note: If not cached, this will download ~500MB-1GB. "
            "Subsequent runs will be fast (cached)."
        )

        # Load tokenizer (checks cache first, downloads if needed)
        _ = AutoTokenizer.from_pretrained(model_name)
        logger.info("✓ Tokenizer loaded")

        # Load model (checks cache first, downloads if needed)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.eval()  # Set to evaluation mode
        logger.info("✓ Model loaded")

        logger.info(f"✓ NLI model '{model_name}' is ready for conflict detection!")
    except Exception:
        logger.exception("Failed to load NLI model")
        logger.warning("Conflict detection will download the model on first use.")
        return False
    else:
        return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    success = preload_nli_model()
    sys.exit(0 if success else 1)
