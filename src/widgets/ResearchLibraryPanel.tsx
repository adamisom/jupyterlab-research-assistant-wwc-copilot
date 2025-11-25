import React, { useState } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { DiscoveryTab } from './DiscoveryTab';
import { LibraryTab } from './LibraryTab';

const ResearchLibraryPanelComponent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'discovery' | 'library'>(
    'discovery'
  );

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-panel">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-tabs">
        <button
          className={`jp-jupyterlab-research-assistant-wwc-copilot-tab ${
            activeTab === 'discovery' ? 'active' : ''
          }`}
          onClick={() => setActiveTab('discovery')}
        >
          Discovery
        </button>
        <button
          className={`jp-jupyterlab-research-assistant-wwc-copilot-tab ${
            activeTab === 'library' ? 'active' : ''
          }`}
          onClick={() => setActiveTab('library')}
        >
          Library
        </button>
      </div>
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-content">
        {activeTab === 'discovery' && <DiscoveryTab />}
        {activeTab === 'library' && <LibraryTab />}
      </div>
    </div>
  );
};

export class ResearchLibraryPanel extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-jupyterlab-research-assistant-wwc-copilot-panel-widget');
    this.id = 'research-library-panel';
    this.title.label = 'Research Library';
    this.title.caption = 'Academic Research Library';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return <ResearchLibraryPanelComponent />;
  }
}
