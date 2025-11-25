import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="jp-WWCExtension-skeleton">
      <div className="jp-WWCExtension-skeleton-title" />
      <div className="jp-WWCExtension-skeleton-line" />
      <div className="jp-WWCExtension-skeleton-line short" />
    </div>
  );
};
