import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { requestAPI } from './request';

/**
 * Initialization data for the jupyterlab-research-assistant-wwc-copilot extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-research-assistant-wwc-copilot:plugin',
  description:
    'A JupyterLab extension for academic research management and WWC quality assessment',
  autoStart: true,
  optional: [ISettingRegistry],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null
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
