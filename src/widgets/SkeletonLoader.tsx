import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-title" />
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line" />
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line short" />
    </div>
  );
};
