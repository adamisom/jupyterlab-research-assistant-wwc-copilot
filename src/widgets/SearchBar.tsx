import React from 'react';

interface ISearchBarProps {
  query: string;
  onQueryChange: (query: string) => void;
  onSearch: () => void;
  isLoading: boolean;
  placeholder?: string;
  additionalInputs?: React.ReactNode;
  searchButtonText?: string;
}

export const SearchBar: React.FC<ISearchBarProps> = ({
  query,
  onQueryChange,
  onSearch,
  isLoading,
  placeholder = 'Search...',
  additionalInputs,
  searchButtonText = 'Search'
}) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
      <input
        type="text"
        value={query}
        onChange={e => onQueryChange(e.target.value)}
        onKeyPress={e => {
          if (e.key === 'Enter') {
            onSearch();
          }
        }}
        placeholder={placeholder}
        className="jp-jupyterlab-research-assistant-wwc-copilot-input"
      />
      {additionalInputs}
      <button
        onClick={onSearch}
        disabled={isLoading || !query.trim()}
        className="jp-jupyterlab-research-assistant-wwc-copilot-button"
      >
        {isLoading ? 'Searching...' : searchButtonText}
      </button>
    </div>
  );
};
