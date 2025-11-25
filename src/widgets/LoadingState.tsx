import React from 'react';
import { SkeletonLoader } from './SkeletonLoader';

interface ILoadingStateProps {
  count?: number;
}

export const LoadingState: React.FC<ILoadingStateProps> = ({ count = 3 }) => {
  return (
    <div>
      {Array.from({ length: count }).map((_, index) => (
        <SkeletonLoader key={index} />
      ))}
    </div>
  );
};
