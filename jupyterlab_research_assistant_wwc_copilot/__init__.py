from pathlib import Path

try:
    from ._version import __version__
except ImportError:
    # Fallback when using the package in dev mode without installing
    # in editable mode with pip. It is highly recommended to install
    # the package from a stable release or in editable mode: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs
    import warnings

    warnings.warn(
        "Importing 'jupyterlab_research_assistant_wwc_copilot' "
        "outside a proper installation.",
        stacklevel=2,
    )
    __version__ = "dev"

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    # Load .env from project root (parent of this package directory)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip .env loading
    pass

from .routes import setup_route_handlers


def _jupyter_labextension_paths():
    return [
        {"src": "labextension", "dest": "jupyterlab-research-assistant-wwc-copilot"}
    ]


def _jupyter_server_extension_points():
    return [{"module": "jupyterlab_research_assistant_wwc_copilot"}]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    setup_route_handlers(server_app.web_app)
    name = "jupyterlab_research_assistant_wwc_copilot"
    server_app.log.info(f"Registered {name} server extension")

    # Pre-load NLI model in background (idempotent - fast if already cached)
    try:
        from .services.conflict_detector import ConflictDetector  # noqa: PLC0415

        # Initialize ConflictDetector in background - this will download/cache the model
        # This is idempotent: if already cached, it loads quickly
        # We do this on startup so the model is ready when users need conflict detection
        def _preload_model():
            try:
                detector = ConflictDetector()
                if detector.model is not None:
                    server_app.log.info(
                        "NLI model pre-loaded and ready for conflict detection"
                    )
                else:
                    server_app.log.warning(
                        "NLI model not available. "
                        "Install transformers library for conflict detection support."
                    )
            except Exception as e:
                server_app.log.warning(f"Could not pre-load NLI model: {e}")
                server_app.log.info(
                    "Model will be downloaded on first conflict detection use"
                )

        # Run in background thread to avoid blocking server startup
        import threading  # noqa: PLC0415

        thread = threading.Thread(target=_preload_model, daemon=True)
        thread.start()
    except ImportError:
        # transformers not available - that's okay, conflict detection is optional
        pass
