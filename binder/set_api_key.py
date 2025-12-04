"""
Helper script to set Semantic Scholar API key for Binder sessions.

Run this in a notebook cell or Python script to set your API key:
    %run binder/set_api_key.py

Or import and use:
    from binder.set_api_key import set_semantic_scholar_key
    set_semantic_scholar_key('your-api-key-here')
"""

import os


def set_semantic_scholar_key(api_key: str):
    """
    Set Semantic Scholar API key as environment variable.

    Args:
        api_key: Your Semantic Scholar API key
    """
    os.environ["SEMANTIC_SCHOLAR_API_KEY"] = api_key
    print("✓ Semantic Scholar API key set successfully!")  # noqa: T201
    print("  Note: You may need to restart the kernel for changes to take effect.")  # noqa: T201


if __name__ == "__main__":
    # For interactive use - prompt for API key
    import getpass

    api_key = getpass.getpass("Enter your Semantic Scholar API key: ")
    if api_key:
        set_semantic_scholar_key(api_key)
    else:
        print("No API key provided.")  # noqa: T201
