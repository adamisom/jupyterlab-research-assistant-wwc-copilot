import React, { useState } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import {
  performMetaAnalysis,
  detectConflicts,
  performSubgroupAnalysis,
  assessPublicationBias,
  performSensitivityAnalysis,
  IMetaAnalysisResult,
  IConflictDetectionResult,
  ISubgroupAnalysisResult,
  IBiasAssessmentResult,
  ISensitivityAnalysisResult
} from '../api';
import { MetaAnalysisView } from './MetaAnalysisView';
import { ConflictView } from './ConflictView';
import { SubgroupAnalysisView } from './SubgroupAnalysisView';
import { BiasAssessmentView } from './BiasAssessmentView';
import { SensitivityAnalysisView } from './SensitivityAnalysisView';
import { showError } from '../utils/notifications';
import { Tabs } from './Tabs';

interface SynthesisWorkbenchProps {
  paperIds: number[];
  onClose?: () => void;
}

type SynthesisTab =
  | 'meta-analysis'
  | 'conflicts'
  | 'subgroups'
  | 'bias'
  | 'sensitivity';

const SynthesisWorkbenchComponent: React.FC<SynthesisWorkbenchProps> = ({
  paperIds,
  onClose
}) => {
  const [activeTab, setActiveTab] = useState<SynthesisTab>('meta-analysis');
  const [metaAnalysisResult, setMetaAnalysisResult] =
    useState<IMetaAnalysisResult | null>(null);
  const [conflictResult, setConflictResult] =
    useState<IConflictDetectionResult | null>(null);
  const [subgroupResult, setSubgroupResult] =
    useState<ISubgroupAnalysisResult | null>(null);
  const [biasResult, setBiasResult] = useState<IBiasAssessmentResult | null>(
    null
  );
  const [sensitivityResult, setSensitivityResult] =
    useState<ISensitivityAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [subgroupVariable, setSubgroupVariable] = useState<string>('');
  const [subgroupAnalysisAttempted, setSubgroupAnalysisAttempted] =
    useState(false);

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

  const handleRunSubgroupAnalysis = async () => {
    if (!subgroupVariable) {
      showError('Subgroup Analysis', 'Please select a subgroup variable');
      return;
    }
    setIsLoading(true);
    setSubgroupAnalysisAttempted(true);
    try {
      const result = await performSubgroupAnalysis(paperIds, subgroupVariable);
      setSubgroupResult(result);
      setActiveTab('subgroups');
    } catch (err) {
      setSubgroupResult(null); // Clear any previous result on error
      showError(
        'Subgroup Analysis Error',
        err instanceof Error ? err.message : 'Unknown error',
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleAssessBias = async () => {
    setIsLoading(true);
    try {
      const result = await assessPublicationBias(paperIds);
      setBiasResult(result);
      setActiveTab('bias');
    } catch (err) {
      showError(
        'Bias Assessment Error',
        err instanceof Error ? err.message : 'Unknown error',
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunSensitivityAnalysis = async () => {
    setIsLoading(true);
    try {
      const result = await performSensitivityAnalysis(paperIds);
      setSensitivityResult(result);
      setActiveTab('sensitivity');
    } catch (err) {
      showError(
        'Sensitivity Analysis Error',
        err instanceof Error ? err.message : 'Unknown error',
        err instanceof Error ? err : undefined
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="jp-WWCExtension-synthesis">
      <div className="jp-WWCExtension-synthesis-header">
        <h2>Synthesis Workbench ({paperIds.length} studies)</h2>
        {onClose && (
          <button onClick={onClose} className="jp-WWCExtension-close">
            ×
          </button>
        )}
      </div>

      <div className="jp-WWCExtension-synthesis-actions">
        <div className="jp-WWCExtension-synthesis-actions-row">
          <button
            onClick={handleRunMetaAnalysis}
            disabled={isLoading}
            className="jp-WWCExtension-button"
          >
            Run Meta-Analysis
          </button>
          <button
            onClick={handleDetectConflicts}
            disabled={isLoading}
            className="jp-WWCExtension-button"
          >
            Detect Conflicts
          </button>
        </div>
        <div className="jp-WWCExtension-synthesis-actions-row">
          <select
            value={subgroupVariable}
            onChange={e => setSubgroupVariable(e.target.value)}
            className="jp-WWCExtension-select"
          >
            <option value="">Select Subgroup Variable...</option>
            <option value="age_group">Age Group</option>
            <option value="intervention_type">Intervention Type</option>
            <option value="learning_domain">Learning Domain</option>
          </select>
          <button
            onClick={handleRunSubgroupAnalysis}
            disabled={isLoading || !subgroupVariable}
            className="jp-WWCExtension-button"
          >
            Run Subgroup Analysis
          </button>
          <button
            onClick={handleAssessBias}
            disabled={isLoading || !metaAnalysisResult}
            className="jp-WWCExtension-button"
          >
            Assess Publication Bias
          </button>
          <button
            onClick={handleRunSensitivityAnalysis}
            disabled={isLoading || !metaAnalysisResult}
            className="jp-WWCExtension-button"
          >
            Sensitivity Analysis
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="jp-WWCExtension-loading">Processing...</div>
      )}

      <Tabs
        tabs={[
          { id: 'meta-analysis', label: 'Meta-Analysis' },
          {
            id: 'conflicts',
            label: 'Conflicts',
            badge: conflictResult?.n_contradictions || 0
          },
          {
            id: 'subgroups',
            label: 'Subgroups',
            badge: subgroupResult ? subgroupResult.n_subgroups : undefined
          },
          { id: 'bias', label: 'Bias Assessment' },
          { id: 'sensitivity', label: 'Sensitivity' }
        ]}
        activeTab={activeTab}
        onTabChange={(tabId: string) => setActiveTab(tabId as SynthesisTab)}
      />

      <div className="jp-WWCExtension-synthesis-content">
        {activeTab === 'meta-analysis' && metaAnalysisResult && (
          <MetaAnalysisView result={metaAnalysisResult} />
        )}
        {activeTab === 'conflicts' && conflictResult && (
          <ConflictView result={conflictResult} />
        )}
        {activeTab === 'subgroups' && subgroupResult && (
          <SubgroupAnalysisView result={subgroupResult} />
        )}
        {activeTab === 'subgroups' && !subgroupResult && (
          <div className="jp-WWCExtension-synthesis-empty">
            {subgroupAnalysisAttempted ? (
              <>
                <h3>No Subgroup Analysis Could Be Performed</h3>
                <p>
                  Subgroup analysis requires at least 2 studies with both effect
                  sizes and the selected subgroup variable metadata. The
                  analysis could not be completed with the current data.
                </p>
                <p>To perform subgroup analysis, ensure your papers have:</p>
                <ul>
                  <li>Effect sizes (run AI extraction if needed)</li>
                  <li>
                    The selected subgroup variable (
                    {subgroupVariable || 'select one above'}) in their metadata
                  </li>
                </ul>
              </>
            ) : (
              <>
                <h3>No Subgroup Analysis Results</h3>
                <p>
                  To run subgroup analysis, select a subgroup variable from the
                  dropdown above and click "Run Subgroup Analysis".
                </p>
                <p>
                  Subgroup analysis requires at least 2 studies with both effect
                  sizes and the selected subgroup variable metadata.
                </p>
              </>
            )}
          </div>
        )}
        {activeTab === 'bias' && biasResult && (
          <BiasAssessmentView result={biasResult} />
        )}
        {activeTab === 'sensitivity' && sensitivityResult && (
          <SensitivityAnalysisView result={sensitivityResult} />
        )}
        {!metaAnalysisResult &&
          !conflictResult &&
          !subgroupResult &&
          !biasResult &&
          !sensitivityResult && (
            <div className="jp-WWCExtension-synthesis-empty">
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
    this.addClass('jp-WWCExtension-synthesis-widget');
    this.id = 'synthesis-workbench';
    this.title.label = 'Synthesis Workbench';
    this.title.caption = 'Meta-Analysis & Conflict Detection';
    this.title.closable = true;
  }

  render(): JSX.Element {
    return <SynthesisWorkbenchComponent paperIds={this.paperIds} />;
  }
}
