import React from 'react';

interface IErrorDisplayProps {
  error: string | null;
}

export const ErrorDisplay: React.FC<IErrorDisplayProps> = ({ error }) => {
  if (!error) {
    return null;
  }

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
      Error: {error}
    </div>
  );
};
