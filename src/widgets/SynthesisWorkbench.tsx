import React, { useState } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import {
  performMetaAnalysis,
  detectConflicts,
  IMetaAnalysisResult,
  IConflictDetectionResult
} from '../api';
import { MetaAnalysisView } from './MetaAnalysisView';
import { ConflictView } from './ConflictView';
import { showError } from '../utils/notifications';
import { Tabs } from './Tabs';

interface SynthesisWorkbenchProps {
  paperIds: number[];
  onClose?: () => void;
}

const SynthesisWorkbenchComponent: React.FC<SynthesisWorkbenchProps> = ({
  paperIds,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<'meta-analysis' | 'conflicts'>(
    'meta-analysis'
  );
  const [metaAnalysisResult, setMetaAnalysisResult] =
    useState<IMetaAnalysisResult | null>(null);
  const [conflictResult, setConflictResult] =
    useState<IConflictDetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRunMetaAnalysis = async () => {
    setIsLoading(true);
    try {
      const result = await performMetaAnalysis(paperIds);
      setMetaAnalysisResult(result);
      setActiveTab('meta-analysis');
    } catch (err) {
      showError(
        'Meta-Analysis Error',
        err instanceof Error ? err.message : 'Unknown error',
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDetectConflicts = async () => {
    setIsLoading(true);
    try {
      const result = await detectConflicts(paperIds);
      setConflictResult(result);
      setActiveTab('conflicts');
    } catch (err) {
      showError(
        'Conflict Detection Error',
        err instanceof Error ? err.message : 'Unknown error',
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-header">
        <h2>Synthesis Workbench ({paperIds.length} studies)</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="jp-jupyterlab-research-assistant-wwc-copilot-close"
          >
            ×
          </button>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-actions">
        <button
          onClick={handleRunMetaAnalysis}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Run Meta-Analysis
        </button>
        <button
          onClick={handleDetectConflicts}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Detect Conflicts
        </button>
      </div>

      {isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-loading">
          Processing...
        </div>
      )}

      <Tabs
        tabs={[
          { id: 'meta-analysis', label: 'Meta-Analysis' },
          {
            id: 'conflicts',
            label: 'Conflicts',
            badge: conflictResult?.n_contradictions || 0
          }
        ]}
        activeTab={activeTab}
        onTabChange={(tabId: string) => setActiveTab(tabId as 'meta-analysis' | 'conflicts')}
      />

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-content">
        {activeTab === 'meta-analysis' && metaAnalysisResult && (
          <MetaAnalysisView result={metaAnalysisResult} />
        )}
        {activeTab === 'conflicts' && conflictResult && (
          <ConflictView result={conflictResult} />
        )}
        {!metaAnalysisResult && !conflictResult && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-synthesis-empty">
            Click "Run Meta-Analysis" or "Detect Conflicts" to begin.
          </div>
        )}
      </div>
    </div>
  );
};

export class SynthesisWorkbench extends ReactWidget {
  private paperIds: number[];

  constructor(paperIds: number[]) {
    super();
    this.paperIds = paperIds;
    this.addClass(
      'jp-jupyterlab-research-assistant-wwc-copilot-synthesis-widget'
    );
    this.id = 'synthesis-workbench';
    this.title.label = 'Synthesis Workbench';
    this.title.caption = 'Meta-Analysis & Conflict Detection';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return <SynthesisWorkbenchComponent paperIds={this.paperIds} />;
  }
}
