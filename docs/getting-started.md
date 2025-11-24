# JupyterLab Development: A Brain-Dead Simple Guide

This is a gentle, step-by-step guide to get your JupyterLab development environment up and running so you can start contributing. No fluff, just the essentials.

---

## The Big Picture: One Repository

JupyterLab is a **monorepo**, which means all the code for its many packages lives in a single GitHub repository. You only need to clone one thing.

- **Repository**: `https://github.com/jupyterlab/jupyterlab`

---

## Step 1: Prerequisites (The Shopping List)

Before you start, make sure you have these installed on your system. This is the most common point of failure, so double-check!

1.  **Git**: To download the code.
2.  **Miniconda** (or Anaconda): To create an isolated Python environment. This is **highly recommended** to avoid messing up your computer's main Python installation.
3.  **Node.js**: The latest LTS (Long-Term Support) version is your safest bet. You can check the required version in the `package.json` file at the root of the JupyterLab repository.

---

## Step 2: The Setup (Step-by-Step)

Follow these commands in order in your terminal.

### 1. Get the Code

First, clone the repository from GitHub and navigate into the new directory.

```bash
# Clone the main JupyterLab repository
git clone https://github.com/jupyterlab/jupyterlab.git

# Go into the new folder
cd jupyterlab
```

### 2. Create a Safe Python Environment

Using `conda`, we'll create a dedicated, clean environment just for this project.

```bash
# Create a new conda environment named "jupyterlab-dev"
# Using conda-forge is important for compatibility
conda create -n jupyterlab-dev -c conda-forge --override-channels python=3.11

# Activate your new environment (you'll need to do this every time you work on the project)
conda activate jupyterlab-dev
```

### 3. Install All Dependencies

JupyterLab has a convenient command that installs everything—both Python and JavaScript packages—at once.

```bash
# This command installs JupyterLab in "editable" mode and all dev dependencies
pip install -e ".[dev]"
```

**What this magic command does:**

- It installs all Python packages listed in the setup files.
- It runs `jlpm install` (JupyterLab's special package manager) to install all the JavaScript dependencies and link the local packages together.

### 4. Build the Project

Now, you need to perform an initial build of the frontend code.

```bash
# This compiles all the TypeScript code into JavaScript
jlpm build
```

---

## Step 3: Run and Test It Out

To see your work, you need to run JupyterLab in a special development mode that watches for code changes.

```bash
# Run JupyterLab in development mode and watch for changes
jupyter lab --dev-mode --watch
```

- `--dev-mode`: This tells JupyterLab to use the local source code you're editing, not the version that might be installed elsewhere on your system.
- `--watch`: This is the magic part. It watches for any changes you make to the frontend (TypeScript/React) code and automatically rebuilds it in the background.

Now, open your web browser to the URL it provides (usually `http://localhost:8888/`). You should see your very own, locally-running JupyterLab!

**To test it:**

1.  Open a code editor (like VS Code) in the `jupyterlab` directory.
2.  Navigate to `packages/ui-components/src/components/Button.tsx`.
3.  Find the `<button>` element and add a simple style change, like `style={{ border: '2px solid red' }}`.
4.  Save the file.
5.  Watch your terminal—you should see the builder recompile.
6.  Refresh your browser. You should now see red borders on JupyterLab's buttons!

If you see the change, you're all set! You have a working development environment and are ready to start building your features.

---

## Appendix: Frequently Asked Questions (FAQ)

Here are answers to common follow-up questions you might have after getting set up.

### Environment & Setup

**1. What if I already have Python/Node.js installed? Do I need to use conda?**

You don't _have_ to, but it's **strongly recommended**. Using a `conda` environment prevents conflicts with other Python projects on your system. It creates a clean, isolated sandbox so you can be sure you're using the exact package versions JupyterLab needs.

**2. How do I know which Node.js version JupyterLab requires?**

Check the `"engines"` field in the `package.json` file at the root of the `jupyterlab` repository. It will specify the required Node.js version range (e.g., `"node": ">=18.0.0"`).

**3. What's the difference between `jlpm` and `npm`?**

`jlpm` is JupyterLab's own wrapper around the `yarn` package manager. It's used to ensure that all packages in the monorepo use the exact same version of dependencies, which is critical for preventing hard-to-debug issues. You should always use `jlpm` instead of `npm` or `yarn` directly when working inside the JupyterLab repo.

**5. What if the build fails? What are common errors?**

- **Error**: `Integrity check failed`. **Fix**: Run `jlpm integrity`. This usually means your local package versions are out of sync.
- **Error**: `node-gyp` build errors. **Fix**: This often means you're missing system-level build tools (like `build-essential` on Linux, or Xcode Command Line Tools on macOS).
- **Error**: Out of memory. **Fix**: The build process can be memory-intensive. Try setting `NODE_OPTIONS=--max-old-space-size=8192` in your terminal before building.

### Development Workflow

**6. How do I run tests locally before submitting a PR?**

From the root of the repository, you can run all tests:

```bash
# Run all TypeScript (Jest) and Python (pytest) tests
jlpm test
```

**8. Do I need to rebuild every time I change Python code, or just TypeScript?**

- **TypeScript/React changes**: No. If you're running in `--watch` mode, the frontend will rebuild automatically in the background. Just save your file and refresh the browser.
- **Python changes**: Yes. You need to restart the JupyterLab server to see changes in your Python backend code.

**9. How do I debug TypeScript/React code in the browser?**

Since you're running in dev mode, you have access to source maps. You can open your browser's developer tools (e.g., Chrome DevTools), go to the "Sources" tab, and find your original `.ts` or `.tsx` files to set breakpoints, inspect variables, and step through your code just like you would with regular JavaScript.

**10. What's the fastest way to iterate on changes?**

Use `--watch` mode! It's designed for rapid iteration. For UI changes, you can often see updates in seconds without a full page reload. For backend changes, a quick server restart is all you need.

### Architecture & Code

**11. Where in the codebase should I put my new extension?**

For this project, you'll be creating a **new, separate repository** for your extension, not adding it directly to the main `jupyterlab` repo. You'll use the official extension template to create the scaffolding, and then you can link it to your local JupyterLab build for development.

**12. How do JupyterLab's packages relate to each other?**

Think of it as a pyramid:

- **Base**: `@lumino/...` packages provide the core widgets and layout system.
- **Mid-level**: `@jupyterlab/...` packages provide core services and components (e.g., `@jupyterlab/apputils`, `@jupyterlab/services`, `@jupyterlab/ui-components`).
- **High-level**: `@jupyterlab/...-extension` packages are "plugins" that take components from the mid-level and add them to the application (e.g., `@jupyterlab/notebook-extension` adds the notebook panel).

**13. What are Lumino widgets and why does JupyterLab use them?**

Lumino is a high-performance widget toolkit that provides the desktop-like feel of JupyterLab. It's responsible for:

- **Layouts**: Docking panels, splitters, tabs, and menus.
- **Messaging**: A system for widgets to communicate with each other without direct dependencies.
- **Performance**: It's designed to handle hundreds of on-screen elements efficiently.

JupyterLab uses Lumino instead of a pure React/Vue/Angular approach because these frameworks are not typically designed for the complex, stateful, desktop-like layouts that JupyterLab requires.

**14. How do I create a new server extension (Python backend)?**

When you create your extension using the official template, it will include a Python package with a `setup.py` file. You'll define a server extension entry point there, which tells JupyterLab to load your Python code on the backend. This is where you'll add your API handlers for things like PDF processing and database queries.

**15. How do I register a new command in the command palette?**

In your frontend code (usually in `plugin.ts`), you'll use the `ICommandPalette` token to get access to the command palette. Then you can use `app.commands.addCommand` to define a new command and `palette.addItem` to make it visible to the user.

### Testing & Quality

**16. How do I run just the tests for my extension, not the whole test suite?**

When you create your extension in its own repository, the `package.json` will have a `test` script. You can simply run `jlpm test` from your extension's directory to run only its tests.

**18. How do I run the linter and formatter before committing?**

The JupyterLab repository (and the extension template) comes with pre-configured scripts:

```bash
# Run the linter
jlpm lint

# Run the formatter
jlpm format
```

**19. What are the pre-commit hooks and how do I set them up?**

Pre-commit hooks are scripts that run automatically before you commit your code, ensuring that you don't accidentally commit poorly formatted or unlinted code. The JupyterLab repo uses a tool called `pre-commit`.

```bash
# Install the pre-commit hooks into your local git repo
pre-commit install
```

After this, every time you run `git commit`, the hooks will run first.

### Contribution Process

**20. Should I open an issue before starting to code, or just submit a PR?**

**Always open an issue first!** This is standard practice for major open-source projects. It allows you to:

- Discuss your proposed feature with maintainers.
- Get feedback on your approach before you write any code.
- Ensure your work aligns with the project's roadmap.

**21. How do I write a good PR description?**

Follow the PR template provided in the repository. A good description includes:

- A link to the issue it resolves.
- A clear summary of the changes.
- A description of how to test the changes manually.
- Screenshots or GIFs of the new UI, if applicable.

**22. What's the typical review timeline?**

It varies, but be patient. Maintainers are often volunteers. A week or two is not uncommon. If you don't hear anything after a couple of weeks, it's okay to post a polite
ping on the PR, like: "@mention-a-maintainer Just wanted to check in on this. Is there anything I can do to help move it forward?"

**23. Can I work on both features in parallel, or should I finish one PR first?**

Finish one PR first! The JupyterLab contribution guide strongly recommends small, incremental PRs. Submit the Research Library feature first. Once it's reviewed and merged, you can submit the Synthesis Engine feature, which will depend on the first one.

### Project-Specific Questions

**24. Where should I create my extension—inside the JupyterLab repo or as a separate repo?**

As a **separate repository**. The main `jupyterlab` repository is for core packages. Third-party extensions, like the one you're building, live in their own repos and are published to `npm` independently. You'll use the [JupyterLab Extension Template](https://github.com/jupyterlab/extension-template) to create your project.

**25. How do I set up the SQLite database for my research library feature?**

Your Python server extension will be responsible for this. You can use a library like `SQLAlchemy` to manage the database. The database file itself (`research_library.db`) can be stored in the user's JupyterLab application data directory, which you can find using `app.paths.user_data_dir`.

**26. What's the best way to integrate Semantic Scholar API calls into the backend?**

Create a new API handler in your Python server extension (e.g., `/api/research/search`). This handler will receive the search query from the frontend, make the request to the Semantic Scholar API using a library like `requests`, and then return the JSON results to the frontend.

**27. How do I add a new sidebar panel to JupyterLab?**

In your frontend plugin, you'll:

1.  Create a new `Widget` (or `ReactWidget`) that contains your UI.
2.  Give it a unique ID, title, and icon.
3.  Use the `app.shell.add(widget, 'left', { rank: 200 });` command to add your widget to the left sidebar. The `rank` option controls its position relative to other icons.
