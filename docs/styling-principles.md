# JupyterLab Extension Styling Guide for the WWC Co-Pilot

## Key Styling Principles (TL;DR)

1.  **Use CSS Variables**: Never hardcode colors, fonts, or spacing. Always use JupyterLab's built-in CSS variables (e.g., `var(--jp-layout-color1)`, `var(--jp-brand-color1)`) to ensure your extension automatically supports light/dark themes and feels native.

2.  **Follow Naming Conventions**: Use the `jp-WidgetName-childElement` and `jp-mod-state` (e.g., `jp-mod-selected`) naming scheme for all your CSS classes. This keeps styles scoped and predictable.

3.  **Leverage UI Components**: Before building a custom component, check if `@jupyterlab/ui-components` already has what you need (e.g., `Button`, `Select`, icons). This saves time and ensures consistency.

4.  **Organize Your Files**: Keep all styles in a `style/` directory with a `base.css` for your custom styles and an `index.css` to import everything.

5.  **Inspect, Don't Invent**: Use your browser's developer tools to inspect core JupyterLab components (like the file browser) to see how they are styled. Copy their patterns.

6.  **Test Both Themes**: Regularly switch between light and dark themes during development to catch styling issues early.

---

This guide provides a comprehensive overview of how to style your WWC Co-Pilot extension to create a professional, user-friendly experience that feels native to JupyterLab.

## 1. The Core Philosophy: Use the System

JupyterLab has a sophisticated styling system based on CSS variables. The number one rule is to **use this system**. Don't reinvent the wheel with custom colors, fonts, or spacing. By using the built-in variables, your extension will:

*   **Automatically support light and dark themes**.
*   **Feel consistent** with the rest of the JupyterLab UI.
*   **Be maintainable** and adapt to future JupyterLab theme changes.

## 2. The CSS Variable System

Here are the key categories of CSS variables you should use. These are defined in the `theme-light-extension` and `theme-dark-extension` packages.

| Category        | Variable Prefix          | Description                                                                 |
| --------------- | ------------------------ | --------------------------------------------------------------------------- |
| **Layout**      | `--jp-layout-color`      | Background colors for different UI regions (0-4).                           |
| **Brand**       | `--jp-brand-color`       | The main JupyterLab accent color (usually blue or orange).                  |
| **Accent**      | `--jp-accent-color`      | Secondary accent colors.                                                    |
| **State**       | `--jp-warn-color`, etc.  | Colors for success, warning, error, and info states.                        |
| **Typography**  | `--jp-ui-font-`          | Font family, sizes, and colors for UI elements.                             |
| **Content**     | `--jp-content-font-`     | Font family, sizes, and colors for content areas like notebooks.            |
| **Borders**     | `--jp-border-`           | Border width, color, and radius.                                            |
| **Elevation**   | `--jp-elevation-z`       | Box shadows for creating depth (Material Design style).                     |

**Example Usage**:
```css
.my-custom-card {
  background-color: var(--jp-layout-color2);
  border: var(--jp-border-width) solid var(--jp-border-color1);
  border-radius: var(--jp-border-radius);
  box-shadow: var(--jp-elevation-z2);
  padding: var(--jp-content-padding);
}
```

## 3. Naming & File Organization

Follow these conventions to keep your styles organized and maintainable.

### File Structure

Your extension's `style/` directory should look like this:

```
style/
├── base.css       # All your custom styles go here
├── index.css      # Imports base.css (often auto-generated)
└── index.js       # Exports index.css for webpack
```

### CSS Class Naming

JupyterLab uses a BEM-like naming convention:

1.  **Widget Class**: `jp-MyWidgetName` (matches the TypeScript class)
2.  **Child Element**: `jp-MyWidgetName-childElement` (e.g., `jp-ResearchLibrary-paperList`)
3.  **State Modifier**: `jp-mod-active`, `jp-mod-selected`, `jp-mod-hover`
4.  **Type Modifier**: `jp-type-directory`, `jp-type-code`

**Example**:
```html
<div class="jp-ResearchLibrary-paperCard jp-mod-selected">
  <h3 class="jp-ResearchLibrary-paperTitle">My Paper</h3>
  <span class="jp-ResearchLibrary-wwcBadge jp-type-meets-standards">Meets Standards</span>
</div>
```

## 4. Styling Ideas for the WWC Co-Pilot

Here are specific, actionable ideas for styling your extension's components.

### Feature 1: Research Library Panel

**Goal**: Make the paper list scannable, informative, and visually appealing.

**`style/base.css`**
```css
/* Main panel styling */
.jp-ResearchLibrary-panel {
  padding: 8px;
  background-color: var(--jp-layout-color1);
}

/* Styling for each paper card in the list */
.jp-ResearchLibrary-paperCard {
  padding: 12px;
  margin-bottom: 8px;
  background-color: var(--jp-layout-color0);
  border-left: 4px solid var(--jp-brand-color2);
  border-radius: var(--jp-border-radius);
  box-shadow: var(--jp-elevation-z1);
  transition: all 0.2s ease-in-out;
}

.jp-ResearchLibrary-paperCard:hover {
  cursor: pointer;
  background-color: var(--jp-layout-color2);
  box-shadow: var(--jp-elevation-z4);
  transform: translateY(-2px);
}

.jp-ResearchLibrary-paperCard.jp-mod-selected {
  border-left-color: var(--jp-brand-color1);
  background-color: var(--jp-layout-color2);
}

/* Title of the paper */
.jp-ResearchLibrary-paperTitle {
  font-size: var(--jp-ui-font-size2);
  font-weight: 600;
  color: var(--jp-ui-font-color1);
  margin-bottom: 4px;
}

/* Authors and year */
.jp-ResearchLibrary-paperMeta {
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-ui-font-color2);
}

/* WWC Status Badge */
.jp-ResearchLibrary-wwcBadge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-top: 8px;
}

.jp-ResearchLibrary-wwcBadge.jp-type-meets-standards {
  background-color: var(--jp-success-color2);
  color: var(--jp-success-color0);
}

.jp-ResearchLibrary-wwcBadge.jp-type-meets-with-reservations {
  background-color: var(--jp-warn-color2);
  color: var(--jp-warn-color0);
}

.jp-ResearchLibrary-wwcBadge.jp-type-does-not-meet {
  background-color: var(--jp-error-color2);
  color: var(--jp-error-color0);
}
```

### Feature 2: Synthesis Workbench

**Goal**: Create a clean, data-driven dashboard for analysis.

**`style/base.css`**
```css
/* Main workbench area */
.jp-SynthesisWorkbench {
  padding: 16px;
  background-color: var(--jp-layout-color1);
}

/* Cards for displaying key stats (e.g., effect size) */
.jp-SynthesisWorkbench-statCard {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background-color: var(--jp-layout-color0);
  border-radius: var(--jp-border-radius);
  box-shadow: var(--jp-elevation-z2);
  text-align: center;
}

.jp-SynthesisWorkbench-statValue {
  font-size: 28px;
  font-weight: 700;
  color: var(--jp-brand-color1);
}

.jp-SynthesisWorkbench-statLabel {
  font-size: 12px;
  color: var(--jp-ui-font-color2);
  text-transform: uppercase;
  margin-top: 4px;
}

/* Container for the forest plot */
.jp-SynthesisWorkbench-forestPlotContainer {
  background-color: white; /* Plots often look best on a white background */
  padding: 24px;
  border-radius: var(--jp-border-radius);
  margin-top: 16px;
  box-shadow: var(--jp-elevation-z2);
}

/* Styling for the WWC Co-Pilot checklist */
.jp-WWCCoPilot-checklistItem {
  display: flex;
  align-items: center;
  padding: 8px;
  border-bottom: var(--jp-border-width) solid var(--jp-border-color2);
}

.jp-WWCCoPilot-checklistItem .jp-mod-checked {
  color: var(--jp-success-color1);
}
```

## 5. Best Practices & Tips

1.  **Inspect Existing Components**: Use your browser's developer tools to inspect core JupyterLab components like the file browser. See what CSS variables and classes they use and copy their patterns.
2.  **Use `ui-components`**: The `@jupyterlab/ui-components` package provides pre-styled React components like `Button`, `InputGroup`, `Select`, and various icons. Use them whenever possible.
3.  **Test in Both Themes**: Regularly switch between the light and dark themes to ensure your styles look good in both.
4.  **Keep it Subtle**: Good design is often invisible. Focus on clear typography, consistent spacing, and subtle visual cues rather than flashy colors or animations.
5.  **Accessibility**: Use `aria-label` attributes and ensure sufficient color contrast. The JupyterLab CSS variables are designed with accessibility in mind.

By following these guidelines, you can create a WWC Co-Pilot extension that not only provides powerful functionality but also looks and feels like a first-class citizen of the JupyterLab ecosystem.

---

**Author**: Manus AI
**Date**: November 25, 2025
**Purpose**: Styling guide for the JupyterLab WWC Co-Pilot extension.
