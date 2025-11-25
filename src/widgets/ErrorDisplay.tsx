import React from 'react';

interface ErrorDisplayProps {
  error: string | null;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error }) => {
  if (!error) {
    return null;
  }

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
      Error: {error}
    </div>
  );
};
