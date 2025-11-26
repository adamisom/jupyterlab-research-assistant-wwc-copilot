# Release Preparation Guide

This guide walks through the complete process of preparing and publishing a release of the JupyterLab Research Assistant & WWC Co-Pilot extension.

## Pre-Release Checklist

Before starting the release process, verify the following:

### Code Quality
- [ ] All tests pass locally (`jlpm test` and `pytest`)
- [ ] All tests pass on CI (check GitHub Actions)
- [ ] Linting passes (`jlpm run lint:check`)
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] No Python syntax errors
- [ ] Code coverage meets project standards

### Documentation
- [ ] README.md is up to date with all features
- [ ] CHANGELOG.md has complete entries for this release
- [ ] All documentation links are valid
- [ ] Code examples in docs are accurate
- [ ] API documentation is complete

### Package Configuration

Run the verification script to check all package configuration:

```bash
python scripts/verify_package_config.py
```

Manual checks:
- [ ] `package.json` version is correct (currently `0.1.0` for initial release)
- [ ] `package.json` has complete metadata (description, author, keywords, URLs)
- [ ] `pyproject.toml` metadata is complete (description, authors, keywords sync from package.json)
- [ ] `install.json` is present and correct
- [ ] License file (LICENSE) is present
- [ ] All dependencies are properly specified in both `package.json` and `pyproject.toml`
- [ ] Keywords in `package.json` are sufficient for discoverability
  - Current keywords: jupyter, jupyterlab, jupyterlab-extension, research, education, meta-analysis, wwc, systematic-review, learning-science, educational-research, cognitive-science, pedagogy, instructional-design, educational-technology

### Functionality
- [ ] Extension installs correctly (`pip install -e .`)
- [ ] Extension appears in JupyterLab (`jupyter labextension list`)
- [ ] Server extension is enabled (`jupyter server extension list`)
- [ ] All features work in a fresh JupyterLab installation
- [ ] No console errors in browser
- [ ] No server errors in logs

### Build Artifacts
- [ ] Extension builds successfully (`jlpm build:prod`)
- [ ] Python package builds (`python -m build`)
- [ ] No build warnings or errors
- [ ] Labextension directory is created correctly

## Release Process

### Option 1: Automated Release (Recommended)

The project uses [Jupyter Releaser](https://github.com/jupyter-server/jupyter_releaser) for automated releases.

#### Prerequisites

1. **GitHub Secrets Configuration:**
   - `NPM_TOKEN`: NPM authentication token (for publishing to npm)
   - GitHub App configured for releases (see Jupyter Releaser docs)

2. **GitHub Variables:**
   - `APP_ID`: GitHub App ID for release automation

3. **PyPI Credentials:**
   - Ensure you have PyPI credentials configured
   - Test upload access: `twine check dist/*`

#### Step 1: Prep Release

1. Go to GitHub Actions → "Step 1: Prep Release"
2. Click "Run workflow"
3. Configure:
   - **Version Spec**: `patch`, `minor`, `major`, or specific version (e.g., `0.1.0`)
   - **Branch**: Usually `main`
   - **Since Last Stable**: Check this to use PRs since last tag
4. Review the draft changelog in the created PR
5. Merge the PR if the changelog looks good

#### Step 2: Publish Release

1. Go to GitHub Actions → "Step 2: Publish Release"
2. Click "Run workflow"
3. Provide the **Release URL** from Step 1
4. The workflow will:
   - Build the extension
   - Publish to npm
   - Publish to PyPI
   - Create GitHub release
   - Tag the repository

#### Verification

After publishing:
- [ ] Check npm: https://www.npmjs.com/package/jupyterlab-research-assistant-wwc-copilot
- [ ] Check PyPI: https://pypi.org/project/jupyterlab-research-assistant-wwc-copilot/
- [ ] Verify GitHub release was created
- [ ] Test installation: `pip install jupyterlab-research-assistant-wwc-copilot`

### Option 2: Manual Release

If automated release is not available, follow these steps:

#### 1. Update Version

```bash
# Update version in package.json (this is the source of truth)
# pyproject.toml will sync automatically via hatch-nodejs-version

# Or use hatch to bump version (creates git tag)
hatch version patch  # or minor, major, or specific version like 0.1.0
```

#### 2. Update CHANGELOG

1. Move entries from `[Unreleased]` to new version section
2. Add release date
3. Commit changes:
   ```bash
   git add CHANGELOG.md package.json
   git commit -m "Bump version to X.Y.Z"
   ```

#### 3. Create Git Tag

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main --tags
```

#### 4. Build Extension

```bash
# Clean previous builds
jlpm clean:all

# Build production version
jlpm build:prod

# Verify build
ls -la jupyterlab_research_assistant_wwc_copilot/labextension/
```

#### 5. Build Python Package

```bash
# Install build tools
pip install build twine

# Build packages
python -m build

# Check packages
twine check dist/*

# Verify contents
ls -la dist/
```

#### 6. Publish to npm

```bash
# Login to npm (if not already)
npm login

# Publish
npm publish --access public
```

#### 7. Publish to PyPI

```bash
# Upload to PyPI (test first with --repository testpypi)
twine upload dist/*

# Or use test PyPI first:
twine upload --repository testpypi dist/*
```

#### 8. Create GitHub Release

1. Go to GitHub → Releases → "Draft a new release"
2. Select the tag you created
3. Title: `v0.1.0` (or your version)
4. Description: Copy from CHANGELOG.md
5. Attach release notes
6. Publish release

## Post-Release Tasks

### 1. Verify Installation

Test the published package:

```bash
# Create fresh environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# Install from PyPI
pip install jupyterlab-research-assistant-wwc-copilot

# Verify installation
jupyter labextension list
jupyter server extension list

# Launch JupyterLab and test extension
jupyter lab
```

### 2. Update Documentation

- [ ] Update any "latest version" references
- [ ] Update installation instructions if needed
- [ ] Add release announcement to project README (if applicable)

### 3. Announce Release

- [ ] Post on JupyterLab Discourse forum
- [ ] Share on relevant social media
- [ ] Update project website (if applicable)
- [ ] Notify users/stakeholders

## JupyterLab Extension Registry

The JupyterLab Extension Registry is a curated list of extensions. To get your extension listed:

### Requirements

1. **Published Packages:**
   - Extension must be published to both npm and PyPI
   - Packages must be installable and functional

2. **Documentation:**
   - Clear README with installation instructions
   - Usage examples
   - Screenshots or demo (recommended)

3. **Code Quality:**
   - Follows JupyterLab extension patterns
   - Proper error handling
   - No security vulnerabilities

4. **License:**
   - Must have an OSI-approved license (BSD-3-Clause is recommended)

### Submission Process

1. **Prepare Submission:**
   - Ensure extension is published and working
   - Prepare a brief description (2-3 sentences)
   - Gather screenshots or demo video

2. **Submit via GitHub:**
   - Open an issue on [jupyterlab/jupyterlab](https://github.com/jupyterlab/jupyterlab)
   - Use the "Extension Registry Request" template
   - Include:
     - Extension name and description
     - Links to npm and PyPI packages
     - Link to GitHub repository
     - Brief use case description
     - Screenshots or demo

3. **Review Process:**
   - JupyterLab maintainers review the submission
   - They verify installation and basic functionality
   - Review typically takes 1-2 weeks
   - You may receive feedback for improvements

4. **After Approval:**
   - Extension appears in JupyterLab's extension manager
   - Users can discover and install via the UI
   - Extension is listed on jupyterlab.readthedocs.io

### Extension Registry Template

When submitting, use this format:

```markdown
## Extension Registry Request

**Extension Name:** jupyterlab-research-assistant-wwc-copilot

**Description:**
A JupyterLab extension for academic research management and WWC quality assessment. 
Provides tools for discovering, importing, and managing academic papers, plus 
rigorous quality assessment and meta-analysis capabilities.

**Links:**
- npm: https://www.npmjs.com/package/jupyterlab-research-assistant-wwc-copilot
- PyPI: https://pypi.org/project/jupyterlab-research-assistant-wwc-copilot/
- GitHub: https://github.com/adamisom/jupyterlab-research-assistant-wwc-copilot

**Use Cases:**
- Education researchers conducting systematic reviews
- Meta-analysts comparing effect sizes across studies
- Researchers managing academic literature in JupyterLab

**Screenshots:**
[Attach screenshots of key features]
```

## Troubleshooting

### Build Failures

- **TypeScript errors**: Run `npx tsc --noEmit` to see all errors
- **Python build errors**: Check `pyproject.toml` syntax
- **Missing dependencies**: Verify all dependencies are in `package.json` and `pyproject.toml`

### Publishing Failures

- **npm publish fails**: Check you're logged in (`npm whoami`)
- **PyPI upload fails**: Verify credentials and package name availability
- **Version conflicts**: Ensure version doesn't already exist on npm/PyPI

### Installation Issues

- **Extension not appearing**: Check `jupyter labextension list`
- **Server extension not enabled**: Run `jupyter server extension enable jupyterlab_research_assistant_wwc_copilot`
- **Import errors**: Verify all dependencies are installed

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

For initial release (0.1.0), this indicates:
- First stable release
- All planned features implemented
- Ready for production use

## Resources

- [Jupyter Releaser Documentation](https://jupyter-releaser.readthedocs.io/)
- [JupyterLab Extension Tutorial](https://jupyterlab.readthedocs.io/en/stable/extension/extension_tutorial.html)
- [PyPI Packaging Guide](https://packaging.python.org/)
- [npm Publishing Guide](https://docs.npmjs.com/packages-and-modules/contributing-packages-to-the-registry)
