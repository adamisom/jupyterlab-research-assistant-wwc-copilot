import React from 'react';

interface SearchBarProps {
  query: string;
  onQueryChange: (query: string) => void;
  onSearch: () => void;
  isLoading: boolean;
  placeholder?: string;
  additionalInputs?: React.ReactNode;
  searchButtonText?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  onQueryChange,
  onSearch,
  isLoading,
  placeholder = 'Search...',
  additionalInputs,
  searchButtonText = 'Search'
}) => {
  return (
    <div className="jp-WWCExtension-search-bar">
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
        className="jp-WWCExtension-input"
      />
      {additionalInputs}
      <button
        onClick={onSearch}
        disabled={isLoading || !query.trim()}
        className="jp-WWCExtension-button"
      >
        {isLoading ? 'Searching...' : searchButtonText}
      </button>
    </div>
  );
};
