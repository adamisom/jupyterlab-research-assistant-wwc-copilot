import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';
import { ILayoutRestorer } from '@jupyterlab/application';
import { WidgetTracker } from '@jupyterlab/apputils';

import { requestAPI } from './request';
import { ResearchLibraryPanel } from './widgets/ResearchLibraryPanel';

/**
 * Initialization data for the jupyterlab-research-assistant-wwc-copilot extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-research-assistant-wwc-copilot:plugin',
  description:
    'A JupyterLab extension for academic research management and WWC quality assessment',
  autoStart: true,
  optional: [ISettingRegistry, ICommandPalette, ILayoutRestorer],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    palette: ICommandPalette | null,
    restorer: ILayoutRestorer | null
  ) => {
    console.log(
      'JupyterLab extension jupyterlab-research-assistant-wwc-copilot is activated!'
    );

    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log(
            'jupyterlab-research-assistant-wwc-copilot settings loaded:',
            settings.composite
          );
        })
        .catch(reason => {
          console.error(
            'Failed to load settings for jupyterlab-research-assistant-wwc-copilot.',
            reason
          );
        });
    }

    // Create and track the research library panel
    const tracker = new WidgetTracker({
      namespace: 'research-library'
    });

    const createPanel = () => {
      const panel = new ResearchLibraryPanel();
      tracker.add(panel);
      app.shell.add(panel, 'left', { rank: 300 });
      return panel;
    };

    // Restore panel if it was open before
    if (restorer) {
      restorer.restore(tracker, {
        command: 'jupyterlab-research-assistant-wwc-copilot:open-library',
        name: () => 'research-library'
      });
    }

    // Register command to open panel
    app.commands.addCommand(
      'jupyterlab-research-assistant-wwc-copilot:open-library',
      {
        label: 'Open Research Library',
        execute: () => {
          const existing = tracker.currentWidget;
          if (existing) {
            app.shell.activateById(existing.id);
          } else {
            createPanel();
          }
        }
      }
    );

    // Add to command palette
    if (palette) {
      palette.addItem({
        command: 'jupyterlab-research-assistant-wwc-copilot:open-library',
        category: 'Research Assistant'
      });
    }

    requestAPI<any>('hello')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The jupyterlab_research_assistant_wwc_copilot server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
