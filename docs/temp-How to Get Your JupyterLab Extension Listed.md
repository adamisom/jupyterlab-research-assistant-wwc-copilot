# How to Get Your JupyterLab Extension Listed

Great news! There is **no formal submission or manual approval process** to get your extension listed in JupyterLab's Extension Manager. Discovery is automatic if you follow the correct packaging standards.

## The Automatic Discovery Process

JupyterLab's Extension Manager searches [PyPI.org](https://pypi.org/) for packages that identify themselves as JupyterLab extensions. If your package is configured correctly, it will automatically appear in the "Discover" section of the Extension Manager.

## The 3 Key Requirements

### 1. Publish to PyPI (Python Package Index)

Your extension's Python package (the backend part) must be published on PyPI. This is what the Extension Manager searches.

### 2. Publish to npm (Node Package Manager)

Your extension's frontend package (the TypeScript/React part) must be published on npm. This is how JupyterLab downloads and installs the frontend code.

### 3. Use the Correct PyPI Classifier (The Magic Step)

This is the most important step. Your Python package's `pyproject.toml` (or `setup.py`) must include a specific "trove classifier" to identify it as a prebuilt JupyterLab extension.

**The required classifier is:**
```
Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt
```

## Step-by-Step Guide

### Step 1: Update Your `pyproject.toml`

Make sure your `pyproject.toml` file has a `classifiers` section that includes the required classifier and its parents. It should look like this:

```toml
[project]
name = "jupyterlab-research-assistant"
# ... other metadata

classifiers = [
    "Framework :: Jupyter",
    "Framework :: Jupyter :: JupyterLab",
    "Framework :: Jupyter :: JupyterLab :: 4",  # Or your supported version
    "Framework :: Jupyter :: JupyterLab :: Extensions",
    "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3",
]
```

### Step 2: Build and Publish Your Packages

Follow the standard process for publishing Python and npm packages:

1.  **Build your extension**:
    ```bash
    pip install jupyter_packaging
    python -m build
    ```

2.  **Publish to PyPI**:
    ```bash
    pip install twine
    twine upload dist/*
    ```

3.  **Publish to npm**:
    ```bash
    npm publish
    ```

### Step 3: Verify Discovery

Once published, your extension should be discoverable:

1.  **On PyPI**: Your package will appear in the official list of [prebuilt JupyterLab extensions](https://pypi.org/search/?c=Framework+%3A%3A+Jupyter+%3A%3A+JupyterLab+%3A%3A+Extensions+%3A%3A+Prebuilt).
2.  **In JupyterLab**: Open the Extension Manager, and your extension should appear in the "Discover" section (it may take some time for the cache to update).

## Optional but Recommended: `install.json`

The official documentation also recommends providing an `install.json` file in your Python package's data to specify the exact package name. The official extension template (`cookiecutter-jupyter-lab-extension`) usually handles this for you automatically.

## What You DON'T Need to Do

-   ❌ Submit a form
-   ❌ Open a pull request to a registry
-   ❌ Get manual approval from the Jupyter team

As long as you follow the packaging standards, the process is completely automated!
