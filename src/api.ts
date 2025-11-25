import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { requestAPI } from './request';
import { retryWithBackoff } from './utils/retry';

// Type definitions matching backend responses
export interface IPaper {
  id?: number;
  paperId?: string;
  title: string;
  authors: string[];
  year?: number;
  doi?: string;
  s2_id?: string;
  citation_count?: number;
  abstract?: string;
  full_text?: string;
  pdf_path?: string;
  study_metadata?: {
    methodology?: string;
    sample_size_baseline?: number;
    sample_size_endline?: number;
    effect_sizes?: Record<string, { d: number; se: number }>;
  };
  learning_science_metadata?: {
    learning_domain?: string;
    intervention_type?: string;
  };
}

export interface IDiscoveryResponse {
  data: IPaper[];
  total: number;
}

export interface IAPIResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

// API functions
export async function getLibrary(): Promise<IPaper[]> {
  const response = await requestAPI<IAPIResponse<IPaper[]>>('library', {
    method: 'GET'
  });

  if (response.status === 'error') {
    throw new Error(response.message || 'Failed to fetch library');
  }

  return response.data || [];
}

export async function searchLibrary(query: string): Promise<IPaper[]> {
  const response = await requestAPI<IAPIResponse<IPaper[]>>(
    `search?q=${encodeURIComponent(query)}`,
    {
      method: 'GET'
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Search failed');
  }

  return response.data || [];
}

export async function searchSemanticScholar(
  query: string,
  year?: string,
  limit: number = 20,
  offset: number = 0
): Promise<IDiscoveryResponse> {
  return retryWithBackoff(async () => {
    const params = new URLSearchParams({ q: query });
    if (year) {
      params.append('year', year);
    }
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await requestAPI<IAPIResponse<IDiscoveryResponse>>(
      `discovery?${params.toString()}`,
      { method: 'GET' }
    );

    if (response.status === 'error') {
      throw new Error(response.message || 'Semantic Scholar search failed');
    }

    return response.data || { data: [], total: 0 };
  });
}

export async function importPaper(paper: IPaper): Promise<IPaper> {
  const response = await requestAPI<IAPIResponse<IPaper>>('library', {
    method: 'POST',
    body: JSON.stringify(paper)
  });

  if (response.status === 'error') {
    throw new Error(response.message || 'Import failed');
  }

  if (!response.data) {
    throw new Error('No data returned from import');
  }

  return response.data;
}

export async function importPDF(file: File): Promise<IPaper> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await requestAPI<IAPIResponse<IPaper>>('import', {
    method: 'POST',
    body: formData
  });

  if (response.status === 'error') {
    throw new Error(response.message || 'PDF import failed');
  }

  if (!response.data) {
    throw new Error('No data returned from import');
  }

  return response.data;
}

export async function exportLibrary(
  format: 'json' | 'csv' | 'bibtex'
): Promise<void> {
  const settings = ServerConnection.makeSettings();
  const url = URLExt.join(
    settings.baseUrl,
    'jupyterlab-research-assistant-wwc-copilot',
    `export?format=${format}`
  );

  const response = await ServerConnection.makeRequest(
    url,
    { method: 'GET' },
    settings
  );

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  // Download file
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `library.${format === 'bibtex' ? 'bib' : format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}
