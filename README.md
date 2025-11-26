# jupyterlab_research_assistant_wwc_copilot

[![Github Actions Status](https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot/workflows/Build/badge.svg)](https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot/actions/workflows/build.yml)

A JupyterLab extension for academic research management and WWC quality assessment

📖 **[User Guide](./USER_GUIDE.md)** - Complete guide for using all extension features

This extension provides two main features:

- **Research Library & Discovery Engine** (Stage 1 - ✅ Complete):
  Discover, import, and manage academic papers with Semantic Scholar and
  OpenAlex integration, PDF parsing, and AI-powered metadata extraction
- **WWC Co-Pilot & Synthesis Engine** (Stage 2 - ✅ Complete): Perform
  rigorous WWC quality assessments, meta-analysis, conflict detection,
  subgroup analysis, publication bias assessment, and sensitivity
  analysis across multiple studies

This extension is composed of a Python package named
`jupyterlab_research_assistant_wwc_copilot` for the server extension
and a NPM package named `jupyterlab-research-assistant-wwc-copilot` for
the frontend extension.

## Requirements

- JupyterLab >= 4.0.0
- Python >= 3.9
- Node.js (for development)

### Optional Dependencies

For advanced features:

- **AI Metadata Extraction**: Requires API keys for Claude, OpenAI, or
  local Ollama instance
- **Paper Discovery**: Semantic Scholar and OpenAlex APIs are used for
  paper discovery. OpenAlex is used as an automatic fallback if Semantic
  Scholar fails or is rate-limited. No API keys required for either service.
- **Conflict Detection**: Requires `transformers` and `torch` libraries
  (optional, can be installed separately)

  To install conflict detection support:

  ```bash
  pip install "jupyterlab-research-assistant-wwc-copilot[conflict-detection]"
  ```

  This will install both `transformers` and `torch` (PyTorch). PyTorch
  is required as the backend for running the NLI models.

  **Note**: The first time you run conflict detection, the NLI model
  (`cross-encoder/nli-deberta-v3-base`) will automatically download
  (~500MB-1GB). This makes the first run slower, but subsequent runs
  will be faster as the model is cached.

  **GPU Support**: By default, conflict detection uses CPU. To use GPU
  instead, modify
  `jupyterlab_research_assistant_wwc_copilot/services/conflict_detector.py`
  and change `device=-1` to `device=0` in the pipeline initialization.

## Install

To install the extension, execute:

```bash
pip install jupyterlab_research_assistant_wwc_copilot
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyterlab_research_assistant_wwc_copilot
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

For development setup, testing, and contribution guidelines, see the
[Developer Guide](./docs/developer-guide.md).

## AI Coding Assistant Support

This project includes an `AGENTS.md` file with coding standards and
best practices for JupyterLab extension development. The file follows
the [AGENTS.md standard](https://agents.md) for cross-tool
compatibility.

### Compatible AI Tools

`AGENTS.md` works with AI coding assistants that support the standard,
including Cursor, GitHub Copilot, Windsurf, Aider, and others. For a
current list of compatible tools, see
[the AGENTS.md standard](https://agents.md). This project also includes
symlinks for tool-specific compatibility:

- `CLAUDE.md` → `AGENTS.md` (for Claude Code)

- `GEMINI.md` → `AGENTS.md` (for Gemini Code Assist)

Other conventions you might encounter:

- `.cursorrules` - Cursor's YAML/JSON format (Cursor also supports AGENTS.md natively)
- `CONVENTIONS.md` / `CONTRIBUTING.md` - For CodeConventions.ai and GitHub bots
- Project-specific rules in JetBrains AI Assistant settings

All tool-specific files should be symlinks to `AGENTS.md` as the single
source of truth.

### What's Included

The `AGENTS.md` file provides guidance on:

- Code quality rules and file-scoped validation commands
- Naming conventions for packages, plugins, and files
- Coding standards (TypeScript, Python)
- Development workflow and debugging
- Backend-frontend integration patterns (`APIHandler`, `requestAPI()`, routing)
- Common pitfalls and how to avoid them

### Customization

You can edit `AGENTS.md` to add project-specific conventions or adjust
guidelines to match your team's practices. The file uses plain Markdown
with Do/Don't patterns and references to actual project files.

**Note**: `AGENTS.md` is living documentation. Update it when you change
conventions, add dependencies, or discover new patterns. Include
`AGENTS.md` updates in commits that modify workflows or coding
standards.

## Documentation

Comprehensive developer documentation is available in the [`docs/`](./docs/) directory:

### Reference Documentation

- **[Master Plan](./docs/master-plan.md)**: High-level project
  architecture and feature breakdown
- **[JupyterLab Architecture](./docs/jupyterlab-architecture.md)**: Deep
  dive into JupyterLab extension patterns
- **[Getting Started](./docs/getting-started.md)**: JupyterLab core
  development environment setup (for understanding JupyterLab, not this
  extension)

### Key Naming Conventions

- **Python package**: `jupyterlab_research_assistant_wwc_copilot`
  (underscores)
- **NPM package**: `jupyterlab-research-assistant-wwc-copilot` (dashes)
- **Plugin ID**: `jupyterlab-research-assistant-wwc-copilot:plugin`
- **Command IDs**:
  `jupyterlab-research-assistant-wwc-copilot:command-name`
- **API Routes**:
  `/jupyterlab-research-assistant-wwc-copilot/endpoint-name`

For detailed development workflow, see the [Developer Guide](./docs/developer-guide.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes.

## Packaging the extension

See [RELEASE.md](RELEASE.md) for release instructions.
