import React, { useState, useMemo } from 'react';
import { IPaper, searchSemanticScholar, importPaper, deletePapers } from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';
import { SearchBar } from './SearchBar';
import { ErrorDisplay } from './ErrorDisplay';
import { LoadingState } from './LoadingState';
import { getPaperKey } from '../utils/paper';

export const DiscoveryTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<IPaper[]>([]);
  const [selectedPapers, setSelectedPapers] = useState<Set<string>>(new Set());
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
      await importPaper(paper);
      showSuccess('Paper Imported', `Successfully imported: ${paper.title}`);
      // Update the paper in results to include the new ID
      setResults(prev => prev.map(p => 
        getPaperKey(p) === getPaperKey(paper) ? { ...p, id: (p.id || paper.id) } : p
      ));
    } catch (err) {
      showError(
        'Import Failed',
        err instanceof Error ? err.message : 'Unknown error occurred',
        err instanceof Error ? err : undefined
      );
    }
  };

  const handleToggleSelection = (paper: IPaper) => {
    const key = getPaperKey(paper);
    setSelectedPapers(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const handleSelectAll = () => {
    if (selectedPapers.size === results.length) {
      // Deselect all
      setSelectedPapers(new Set());
    } else {
      // Select all
      setSelectedPapers(new Set(results.map(p => getPaperKey(p))));
    }
  };

  const handleDelete = async () => {
    const papersToDelete = results.filter(p => 
      selectedPapers.has(getPaperKey(p)) && p.id
    );

    if (papersToDelete.length === 0) {
      showError('Delete Failed', 'No imported papers selected for deletion');
      return;
    }

    const paperIds = papersToDelete.map(p => p.id!).filter((id): id is number => id !== undefined);
    
    if (paperIds.length === 0) {
      showError('Delete Failed', 'Selected papers are not in the library yet');
      return;
    }

    try {
      const result = await deletePapers(paperIds);
      showSuccess('Papers Deleted', `Successfully deleted ${result.deleted_count} paper(s)`);
      
      // Remove deleted papers from results
      setResults(prev => prev.filter(p => !paperIds.includes(p.id!)));
      // Clear selections
      setSelectedPapers(new Set());
    } catch (err) {
      showError(
        'Delete Failed',
        err instanceof Error ? err.message : 'Unknown error occurred',
        err instanceof Error ? err : undefined
      );
    }
  };

  const selectedCount = selectedPapers.size;
  const deletableCount = useMemo(() => 
    results.filter(p => selectedPapers.has(getPaperKey(p)) && p.id).length,
    [results, selectedPapers]
  );

  return (
    <div className="jp-WWCExtension-discovery">
      <SearchBar
        query={query}
        onQueryChange={setQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        placeholder="Search Semantic Scholar / OpenAlex..."
      />

      {results.length > 0 && (
        <div className="jp-WWCExtension-discovery-actions" style={{ margin: '10px 0', display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={handleSelectAll}
            className="jp-WWCExtension-button"
          >
            {selectedCount === results.length ? 'Deselect All' : 'Select All'}
          </button>
          {selectedCount > 0 && deletableCount > 0 && (
            <button
              onClick={handleDelete}
              className="jp-WWCExtension-button jp-mod-warn"
              style={{ marginLeft: 'auto' }}
            >
              Delete {deletableCount} from Library
            </button>
          )}
        </div>
      )}

      <ErrorDisplay error={error} />

      {isLoading && <LoadingState />}

      {!isLoading && (
        <div className="jp-WWCExtension-results">
          {results.map(paper => (
            <PaperCard
              key={getPaperKey(paper)}
              paper={paper}
              onImport={() => handleImport(paper)}
              selected={selectedPapers.has(getPaperKey(paper))}
              onToggleSelection={() => handleToggleSelection(paper)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
