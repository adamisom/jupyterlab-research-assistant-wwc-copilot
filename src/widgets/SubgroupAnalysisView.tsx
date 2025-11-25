import React from 'react';
import { ISubgroupAnalysisResult } from '../api';
import { MetaAnalysisView } from './MetaAnalysisView';

interface SubgroupAnalysisViewProps {
  result: ISubgroupAnalysisResult;
}

export const SubgroupAnalysisView: React.FC<SubgroupAnalysisViewProps> = ({
  result
}) => {
  return (
    <div className="jp-WWCExtension-subgroup-analysis">
      <h3>Subgroup Analysis: {result.subgroup_variable}</h3>

      {/* Overall Results */}
      <div className="jp-WWCExtension-subgroup-overall">
        <h4>Overall Meta-Analysis (All Studies)</h4>
        <MetaAnalysisView result={result.overall} />
      </div>

      {/* Subgroup Results */}
      <div className="jp-WWCExtension-subgroup-results">
        <h4>Results by Subgroup</h4>
        {Object.entries(result.subgroups).map(
          ([subgroupName, subgroupResult]) => (
            <div key={subgroupName} className="jp-WWCExtension-subgroup-item">
              <h5>
                {subgroupName} (n={subgroupResult.n_studies})
              </h5>
              <MetaAnalysisView result={subgroupResult} />
            </div>
          )
        )}
      </div>
    </div>
  );
};
