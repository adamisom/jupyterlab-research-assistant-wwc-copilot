import React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { LibraryTab } from './LibraryTab';

const ResearchLibraryPanelComponent: React.FC = () => {
  return (
    <div className="jp-WWCExtension-panel">
      <div className="jp-WWCExtension-content">
        <LibraryTab />
      </div>
    </div>
  );
};

export class ResearchLibraryPanel extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-WWCExtension-panel-widget');
    this.id = 'research-library-panel';
    this.title.label = 'Research Library';
    this.title.caption = 'Academic Research Library';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return <ResearchLibraryPanelComponent />;
  }
}
