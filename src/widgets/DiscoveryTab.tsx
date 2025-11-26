import React, { useState } from 'react';
import { IPaper, searchSemanticScholar, importPaper } from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';
import { SearchBar } from './SearchBar';
import { ErrorDisplay } from './ErrorDisplay';
import { LoadingState } from './LoadingState';
import { getPaperKey } from '../utils/paper';

export const DiscoveryTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<IPaper[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await searchSemanticScholar(query, 20);
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleImport = async (paper: IPaper) => {
    try {
      const result = await importPaper(paper);
      if (result.is_duplicate) {
        showSuccess(
          'Paper Already in Library',
          `"${paper.title}" is already in your library.`
        );
      } else {
        showSuccess('Paper Imported', `Successfully imported: ${paper.title}`);
      }
    } catch (err) {
      showError(
        'Import Failed',
        err instanceof Error ? err.message : 'Unknown error occurred',
        err instanceof Error ? err : undefined
      );
    }
  };

  return (
    <div className="jp-WWCExtension-discovery">
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search Semantic Scholar / OpenAlex..."
      />

      <ErrorDisplay error={error} />

      {isLoading && <LoadingState />}

      {!isLoading && (
        <div className="jp-WWCExtension-results">
          {results.map(paper => (
            <PaperCard
              key={getPaperKey(paper)}
              paper={paper}
              onImport={() => handleImport(paper)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
