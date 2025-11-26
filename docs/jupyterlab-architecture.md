# JupyterLab Architecture Deep Dive for the WWC Co-Pilot

This guide provides a comprehensive overview of the JupyterLab architecture, specifically tailored to building your WWC Co-Pilot extension. It covers the high-level structure, key directories, design patterns, and specific examples relevant to your project.

## 1. High-Level Architecture Overview

JupyterLab is a modular, extensible web application built on a frontend-backend architecture:

- **Frontend**: A single-page application written in TypeScript, using React for UI components and Lumino for the underlying widget and messaging system.
- **Backend**: A Jupyter Server extension written in Python, providing REST APIs for file access, kernel management, and other services.

### The Monorepo Structure

The `jupyterlab/jupyterlab` repository is a **monorepo** managed with Lerna and Yarn workspaces. It contains over 100 individual TypeScript packages in the `packages/` directory. This structure allows for code sharing and consistent dependency management across the entire project.

### Key Architectural Concepts

- **Plugins**: The fundamental unit of extension. Everything in JupyterLab is a plugin, including core features like the file browser and notebook.
- **Services & Tokens**: A dependency injection system where plugins can provide and consume services using unique `Token` identifiers.
- **Lumino Widgets**: The foundation of the UI. Lumino provides a high-performance widget system with features like drag-and-drop, custom layouts, and messaging.
- **Server Extensions**: The mechanism for adding backend functionality to JupyterLab with custom Python handlers.

## 2. Key Directories & Their Purposes

When exploring the JupyterLab codebase, these are the most important directories to understand:

| Directory             | Purpose                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| `packages/`           | **The heart of the frontend**. Contains all the individual TypeScript packages that make up JupyterLab. |
| `jupyterlab/`         | **The core Python package**. Contains the server extension, application entry point, and build tools.   |
| `jupyterlab/handlers` | Python API handlers for the backend server.                                                             |
| `examples/`           | Example extensions that demonstrate various features and integration points.                            |
| `testutils/`          | Utilities for testing JupyterLab extensions.                                                            |

## 3. The "Component + Extension" Pattern

JupyterLab follows a common pattern where a feature is split into two packages:

1. **Component Package** (e.g., `@jupyterlab/filebrowser`):
    - Contains the core UI widgets, data models, and logic.
    - Is framework-agnostic (doesn't depend on the JupyterLab application shell).
    - Can be used in other applications outside of JupyterLab.

2. **Extension Package** (e.g., `@jupyterlab/filebrowser-extension`):
    - Integrates the component package into JupyterLab.
    - Registers commands, adds widgets to the shell, and connects to other services.
    - Depends on the JupyterLab application shell.

**For your project**: Your `jupyterlab-research-assistant` extension will follow this pattern. The core logic for your Research Library and Synthesis Engine will be in component packages, and the main extension package will integrate them into JupyterLab.

## 4. Pattern Cheat Sheet for the WWC Co-Pilot

Here are the key patterns you will use, with specific examples relevant to your project.

### Pattern 1: Creating a Sidebar Panel (for the Research Library)

**Goal**: Add a new panel to the left sidebar to display the research library.

**Key Files to Study**:

- `packages/running-extension/src/index.ts`
- `packages/toc-extension/src/index.ts`

**Code Pattern**:

```typescript
import { ReactWidget, WidgetTracker } from '@jupyterlab/apputils';
import { ILabShell, ILayoutRestorer } from '@jupyterlab/application';
import { LabIcon } from '@jupyterlab/ui-components';

// 1. Create your React component for the panel content
const ResearchLibraryComponent = () => {
  return <div>My Research Library</div>;
};

// 2. Create a Lumino widget to wrap your React component
class ResearchLibraryWidget extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-ResearchLibraryWidget');
  }

  render(): JSX.Element {
    return <ResearchLibraryComponent />;
  }
}

// 3. In your plugin's activate function:
const activate = (app: JupyterFrontEnd, restorer: ILayoutRestorer | null) => {
  const widget = new ResearchLibraryWidget();
  widget.id = 'research-library-panel';
  widget.title.icon = myCustomIcon; // Use a custom LabIcon
  widget.title.caption = 'Research Library';

  // 4. Add the widget to the left sidebar
  app.shell.add(widget, 'left', { rank: 300 });

  // 5. Use WidgetTracker to track the panel's state
  const tracker = new WidgetTracker({ namespace: 'research-library' });
  tracker.add(widget);

  // 6. Use ILayoutRestorer to restore the panel on page load
  if (restorer) {
    restorer.restore(tracker, {
      command: 'apputils:activate-command-by-id',
      args: { id: 'research-library-panel' },
      name: () => 'research-library'
    });
  }
};
```

### Pattern 2: Creating a Server Extension API (for PDF processing, database access)

**Goal**: Create a Python backend to handle file uploads, run AI metadata extraction, and query the SQLite database.

**Key Files to Study**:

- `jupyterlab/handlers/announcements.py`
- `jupyterlab/serverextension.py`

**Code Pattern**:

**`jupyterlab_research_assistant/handlers.py`**

```python
from jupyter_server.base.handlers import APIHandler
import tornado
import json

class LibraryHandler(APIHandler):
    @tornado.web.authenticated
    async def get(self):
        # Logic to get all papers from the database
        papers = await self.db_manager.get_all_papers()
        self.finish(json.dumps(papers))

    @tornado.web.authenticated
    async def post(self):
        # Logic to add a new paper
        data = self.get_json_body()
        new_paper = await self.db_manager.add_paper(data)
        self.set_status(201)
        self.finish(json.dumps(new_paper))
```

**`jupyterlab_research_assistant/__init__.py`**

```python
from .handlers import LibraryHandler

def _jupyter_server_extension_points():
    return [{
        "module": "jupyterlab_research_assistant"
    }]

def _load_jupyter_server_extension(server_app):
    """Register the API handler with the Jupyter Server."""
    web_app = server_app.web_app
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "research-assistant", "library")
    handlers = [(route_pattern, LibraryHandler)]
    web_app.add_handlers(host_pattern, handlers)
```

### Pattern 3: Using Tokens for Dependency Injection

**Goal**: Define a service for your research library and allow other plugins to access it.

**Key Files to Study**:

- `packages/filebrowser/src/tokens.ts`

**Code Pattern**:

**`src/tokens.ts`**

```typescript
import { Token } from '@lumino/coreutils';

// 1. Define the token
export const IResearchLibrary = new Token<IResearchLibrary>(
  '@wwc-copilot/research-assistant:IResearchLibrary'
);

// 2. Define the interface
export interface IResearchLibrary {
  search(query: string): Promise<any[]>;
  addPaper(file: File): Promise<any>;
}
```

**`src/index.ts` (providing the service)**

```typescript
const libraryPlugin: JupyterFrontEndPlugin<IResearchLibrary> = {
  id: '@wwc-copilot/research-assistant:library-service',
  provides: IResearchLibrary,
  activate: (app: JupyterFrontEnd): IResearchLibrary => {
    // Implementation of the service
    return new ResearchLibraryManager();
  }
};
```

**`src/other-plugin.ts` (consuming the service)**

```typescript
const otherPlugin: JupyterFrontEndPlugin<void> = {
  id: '@wwc-copilot/other-plugin',
  requires: [IResearchLibrary],
  activate: (app: JupyterFrontEnd, library: IResearchLibrary) => {
    // Use the library service
    library.search('meta-analysis');
  }
};
```

## 5. Architecture Diagram for the WWC Co-Pilot

See the [architecture diagram](./architecture.mmd) for a visual representation of the WWC Co-Pilot system architecture.

## 6. Specific Examples for the WWC Co-Pilot Features

### Feature 1: Research Library Panel

**What you're building**: A sidebar panel that displays imported papers, allows search/filtering, and provides a "Discovery" tab for Semantic Scholar integration.

**Key patterns to use**:

1. **Sidebar Panel Pattern** (see Pattern 1 above)
2. **API Client Pattern** for calling your backend
3. **State Management** using Lumino signals or React state

**Directory structure in your extension**:

```
src/
├── index.ts                    # Main plugin registration
├── library/
│   ├── widget.tsx              # ResearchLibraryWidget (Lumino + React)
│   ├── components/
│   │   ├── PaperList.tsx       # List of papers
│   │   ├── SearchBar.tsx       # Search/filter UI
│   │   └── DiscoveryTab.tsx    # Semantic Scholar search
│   └── model.ts                # Data model for library state
└── api.ts                      # API client for backend calls
```

**Code snippet for calling your backend**:

```typescript
import { ServerConnection } from '@jupyterlab/services';

export class ResearchLibraryAPI {
  async getPapers(): Promise<any[]> {
    const settings = ServerConnection.makeSettings();
    const url = `${settings.baseUrl}research-assistant/library`;

    const response = await ServerConnection.makeRequest(url, {}, settings);
    if (!response.ok) {
      throw new Error('Failed to fetch papers');
    }
    return await response.json();
  }

  async addPaper(file: File): Promise<any> {
    const settings = ServerConnection.makeSettings();
    const url = `${settings.baseUrl}research-assistant/import`;

    const formData = new FormData();
    formData.append('file', file);

    const response = await ServerConnection.makeRequest(
      url,
      {
        method: 'POST',
        body: formData
      },
      settings
    );

    if (!response.ok) {
      throw new Error('Failed to import paper');
    }
    return await response.json();
  }
}
```

### Feature 2: Synthesis Workbench

**What you're building**: A main area widget that opens when a user selects papers for synthesis. It includes the WWC Co-Pilot, meta-analysis tools, and conflict detection.

**Key patterns to use**:

1. **Main Area Widget Pattern** (similar to notebooks)
2. **Tabbed Interface** for different synthesis views (WWC, Meta-Analysis, Conflicts)
3. **Toolbar** with action buttons

**Code snippet for opening in main area with tabs and toolbar**:

```typescript
import { ReactWidget, Toolbar, ToolbarButton } from '@jupyterlab/apputils';
import { TabPanel, Widget } from '@lumino/widgets';
import { runIcon, stopIcon } from '@jupyterlab/ui-components';

// Create a main widget with tabs
class SynthesisWorkbenchWidget extends Widget {
  constructor(paperIds: number[]) {
    super();
    this.addClass('jp-SynthesisWorkbench');

    // 1. Create toolbar
    const toolbar = new Toolbar();
    toolbar.addItem(
      'run-synthesis',
      new ToolbarButton({
        icon: runIcon,
        onClick: () => this.runSynthesis(),
        tooltip: 'Run Synthesis'
      })
    );
    toolbar.addItem(
      'export',
      new ToolbarButton({
        icon: stopIcon,
        onClick: () => this.exportResults(),
        tooltip: 'Export Results'
      })
    );

    // 2. Create tab panel
    const tabPanel = new TabPanel();

    // 3. Add tabs for different views
    const wwcTab = new WWCCoPilotWidget(paperIds);
    wwcTab.title.label = 'WWC Quality';
    tabPanel.addWidget(wwcTab);

    const metaAnalysisTab = new MetaAnalysisWidget(paperIds);
    metaAnalysisTab.title.label = 'Meta-Analysis';
    tabPanel.addWidget(metaAnalysisTab);

    const conflictsTab = new ConflictDetectionWidget(paperIds);
    conflictsTab.title.label = 'Conflicts';
    tabPanel.addWidget(conflictsTab);

    // 4. Layout: toolbar on top, tabs below
    this.layout = new PanelLayout();
    (this.layout as PanelLayout).addWidget(toolbar);
    (this.layout as PanelLayout).addWidget(tabPanel);
  }

  private runSynthesis(): void {
    // Synthesis logic
  }

  private exportResults(): void {
    // Export logic
  }
}

// In your command handler
app.commands.addCommand('research-assistant:open-synthesis', {
  label: 'Open Synthesis Workbench',
  execute: (args: { paperIds: number[] }) => {
    const widget = new SynthesisWorkbenchWidget(args.paperIds);
    widget.id = `synthesis-${Date.now()}`;
    widget.title.label = 'Synthesis Workbench';
    widget.title.closable = true;

    // Add to main area (not sidebar)
    app.shell.add(widget, 'main');

    // Activate it
    app.shell.activateById(widget.id);
  }
});
```

## 7. Testing Your Extension

JupyterLab uses Jest for frontend tests and pytest for backend tests.

### Frontend Testing Pattern

**`src/__tests__/library.spec.ts`**

```typescript
import { ResearchLibraryWidget } from '../library/widget';

describe('ResearchLibraryWidget', () => {
  it('should render without crashing', () => {
    const widget = new ResearchLibraryWidget();
    expect(widget).toBeTruthy();
  });

  it('should display papers', async () => {
    const widget = new ResearchLibraryWidget();
    // Mock API response
    const papers = [{ id: 1, title: 'Test Paper' }];
    widget.model.papers = papers;

    // Assert that the paper is displayed
    expect(widget.node.textContent).toContain('Test Paper');
  });
});
```

### Backend Testing Pattern

**`jupyterlab_research_assistant/tests/test_handlers.py`**

```python
import pytest
from unittest.mock import Mock

async def test_library_handler_get(jp_fetch):
    # jp_fetch is a pytest fixture provided by jupyter_server
    response = await jp_fetch('research-assistant', 'library')
    assert response.code == 200
    data = json.loads(response.body)
    assert isinstance(data, list)
```

## 8. Key Directories in the JupyterLab Monorepo

Here's a quick reference for the most important packages in the `packages/` directory that you should study:

| Package                       | Purpose                                                      | Relevance to WWC Co-Pilot                                                          |
| ----------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `@jupyterlab/application`     | Core application shell, plugin system                        | **Critical**: You'll use `JupyterFrontEnd` and `JupyterFrontEndPlugin` everywhere. |
| `@jupyterlab/apputils`        | Common UI utilities (dialogs, toolbars, widgets)             | **High**: Use `ReactWidget`, `Dialog`, `showErrorMessage`.                         |
| `@jupyterlab/services`        | API clients for Jupyter Server (kernels, contents, sessions) | **High**: Use `ServerConnection` for your custom API calls.                        |
| `@jupyterlab/filebrowser`     | File browser widget and model                                | **High**: Study this for the sidebar panel pattern.                                |
| `@jupyterlab/running`         | Running sessions sidebar                                     | **High**: Another great example of a sidebar panel.                                |
| `@jupyterlab/notebook`        | Notebook widget and model                                    | **Medium**: Study for main area widget patterns.                                   |
| `@jupyterlab/ui-components`   | Reusable UI components (icons, buttons, menus)               | **High**: Use `LabIcon`, `CommandToolbarButton`, etc.                              |
| `@jupyterlab/settingregistry` | Settings management                                          | **Medium**: For user preferences (e.g., AI provider choice).                       |
| `@jupyterlab/statedb`         | Persistent state storage                                     | **Medium**: For remembering panel state across sessions.                           |
| `@jupyterlab/translation`     | Internationalization (i18n)                                  | **Low**: Optional, but good practice for accessibility.                            |

## 9. Common Pitfalls & How to Avoid Them

### Pitfall 1: Not Understanding Lumino Widgets

**Problem**: Trying to use React patterns directly without wrapping in Lumino widgets.

**Solution**: Always use `ReactWidget` from `@jupyterlab/apputils` to wrap your React components. Lumino handles the lifecycle, layout, and messaging.

### Pitfall 2: Forgetting to Register Commands

**Problem**: Your UI buttons don't do anything because the commands aren't registered.

**Solution**: Always register commands in your plugin's `activate` function before adding UI elements that reference them.

### Pitfall 3: Not Handling Async Operations Properly

**Problem**: Backend calls block the UI or fail silently.

**Solution**: Always use `async/await` and wrap API calls in try/catch blocks. Show loading indicators and error messages to the user.

### Pitfall 4: Hardcoding URLs

**Problem**: Your extension breaks when deployed because URLs are hardcoded.

**Solution**: Always use `ServerConnection.makeSettings()` to get the correct base URL.

## 10. Next Steps: From Guide to Code

Now that you understand the architecture, here's your action plan:

1. **Set up your extension** using the cookiecutter template (as described in the getting started guide).
2. **Study the filebrowser and running extensions** in the JupyterLab repo. These are your best references.
3. **Start with the Research Library panel**. Get a basic sidebar panel working first, even if it just displays "Hello World".
4. **Add the backend handler**. Create a simple `/library` endpoint that returns hardcoded data.
5. **Connect frontend to backend**. Use `ServerConnection.makeRequest` to fetch data from your handler.
6. **Iterate**. Add features incrementally: search, import, Semantic Scholar, etc.
7. **Test continuously**. Write tests as you go, not at the end.

## 11. Resources & References

- **Official JupyterLab Extension Tutorial**: <https://jupyterlab.readthedocs.io/en/latest/extension/extension_tutorial.html>
- **Lumino Documentation**: <https://lumino.readthedocs.io/>
- **JupyterLab GitHub Repository**: <https://github.com/jupyterlab/jupyterlab>
- **Extension Examples**: <https://github.com/jupyterlab/extension-examples>

---

**Author**: Manus AI
**Date**: November 24, 2025
**Purpose**: Architecture guide for the JupyterLab WWC Co-Pilot extension project
