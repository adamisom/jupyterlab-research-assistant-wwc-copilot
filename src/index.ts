import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette, WidgetTracker } from '@jupyterlab/apputils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { Dialog, showDialog } from '@jupyterlab/apputils';
import { requestAPI } from './request';
import { ResearchLibraryPanel } from './widgets/ResearchLibraryPanel';
import { exportLibrary, importPDF } from './api';
import { showError, showSuccess } from './utils/notifications';

/**
 * Initialization data for the jupyterlab-research-assistant-wwc-copilot extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-research-assistant-wwc-copilot:plugin',
  description:
    'A JupyterLab extension for academic research management and WWC quality assessment',
  autoStart: true,
  optional: [
    ISettingRegistry,
    ICommandPalette,
    ILayoutRestorer,
    IFileBrowserFactory
  ],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    palette: ICommandPalette | null,
    restorer: ILayoutRestorer | null,
    fileBrowserFactory: IFileBrowserFactory | null
  ) => {
    console.log(
      'JupyterLab extension jupyterlab-research-assistant-wwc-copilot is activated!'
    );

    // Store settings for use in commands
    let aiConfig: any = null;
    if (settingRegistry) {
      settingRegistry
        .load(plugin.id)
        .then(settings => {
          console.log(
            'jupyterlab-research-assistant-wwc-copilot settings loaded:',
            settings.composite
          );
          // Extract AI extraction config
          const composite = settings.composite as any;
          if (composite.aiExtraction) {
            aiConfig = composite.aiExtraction;
          }
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

    // Register import-pdf command
    app.commands.addCommand(
      'jupyterlab-research-assistant-wwc-copilot:import-pdf',
      {
        label: 'Import PDF to Research Library',
        execute: async () => {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = '.pdf,application/pdf';
          input.onchange = async (e: Event) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
              try {
                await importPDF(file, aiConfig);
                showSuccess(
                  'PDF Imported',
                  `Successfully imported: ${file.name}`
                );
                // Refresh library if panel is open
                const panel = tracker.currentWidget;
                if (panel) {
                  // Trigger refresh - would need to expose a method on the panel
                }
              } catch (err) {
                showError(
                  'Import Failed',
                  err instanceof Error ? err.message : 'Unknown error'
                );
              }
            }
          };
          input.click();
        }
      }
    );

    // Register export-library command
    app.commands.addCommand(
      'jupyterlab-research-assistant-wwc-copilot:export-library',
      {
        label: 'Export Research Library',
        execute: async () => {
          // Show a dialog to select format
          const format = await showDialog({
            title: 'Export Library',
            body: 'Select export format:',
            buttons: [
              Dialog.cancelButton(),
              Dialog.okButton({ label: 'JSON' }),
              Dialog.okButton({ label: 'CSV' }),
              Dialog.okButton({ label: 'BibTeX' })
            ]
          });

          if (format.button.accept && format.button.label) {
            const formatMap: Record<string, 'json' | 'csv' | 'bibtex'> = {
              JSON: 'json',
              CSV: 'csv',
              BibTeX: 'bibtex'
            };
            const exportFormat = formatMap[format.button.label] || 'json';
            try {
              await exportLibrary(exportFormat);
              showSuccess(
                'Export Complete',
                `Library exported as ${exportFormat.toUpperCase()}`
              );
            } catch (err) {
              showError(
                'Export Failed',
                err instanceof Error ? err.message : 'Unknown error'
              );
            }
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
      palette.addItem({
        command: 'jupyterlab-research-assistant-wwc-copilot:import-pdf',
        category: 'Research Assistant'
      });
      palette.addItem({
        command: 'jupyterlab-research-assistant-wwc-copilot:export-library',
        category: 'Research Assistant'
      });
    }

    // Note: Main menu integration removed - JupyterLab 4 doesn't expose IMainMenu
    // Commands are available via command palette and keyboard shortcuts

    // Add file browser context menu
    if (fileBrowserFactory) {
      app.commands.addCommand(
        'jupyterlab-research-assistant-wwc-copilot:import-pdf-from-browser',
        {
          label: 'Import to Research Library',
          execute: async args => {
            const path = (args as any).path as string;
            if (!path || !path.endsWith('.pdf')) {
              return;
            }

            try {
              // Read file from filesystem using file browser
              const fileBrowser = fileBrowserFactory.tracker.currentWidget;
              if (!fileBrowser) {
                throw new Error('File browser not available');
              }
              const contents = fileBrowser.model.manager.services.contents;
              const fileData = await contents.get(path, {
                type: 'file',
                format: 'base64'
              });

              // Convert base64 to File object
              const binaryString = atob(fileData.content);
              const bytes = new Uint8Array(binaryString.length);
              for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
              }
              const blob = new Blob([bytes], { type: 'application/pdf' });
              const pdfFile = new File([blob], fileData.name, {
                type: 'application/pdf'
              });

              await importPDF(pdfFile, aiConfig);
              showSuccess(
                'PDF Imported',
                `Successfully imported: ${fileData.name}`
              );
            } catch (err) {
              showError(
                'Import Failed',
                err instanceof Error ? err.message : 'Unknown error'
              );
            }
          },
          isEnabled: args => {
            const path = (args as any).path as string;
            return path ? path.endsWith('.pdf') : false;
          }
        }
      );

      // Add to file browser context menu for PDF files
      // The selector targets PDF files in the directory listing
      app.contextMenu.addItem({
        command:
          'jupyterlab-research-assistant-wwc-copilot:import-pdf-from-browser',
        selector: '.jp-DirListing-item[data-file-type="pdf"]',
        rank: 10
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
