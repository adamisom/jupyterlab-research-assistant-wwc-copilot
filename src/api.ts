import { URLExt } from '@jupyterlab/coreutils';
import { ServerConnection } from '@jupyterlab/services';
import { requestAPI } from './request';
import { retryWithBackoff } from './utils/retry';
import { handleAPIResponse } from './utils/api-response';

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

  const data = handleAPIResponse(response, 'Failed to fetch library');
  return data || [];
}

export async function searchLibrary(query: string): Promise<IPaper[]> {
  const response = await requestAPI<IAPIResponse<IPaper[]>>(
    `search?q=${encodeURIComponent(query)}`,
    {
      method: 'GET'
    }
  );

  const data = handleAPIResponse(response, 'Search failed');
  return data || [];
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

    return (
      handleAPIResponse(response, 'Semantic Scholar search failed') || {
        data: [],
        total: 0
      }
    );
  });
}

export async function importPaper(paper: IPaper): Promise<IPaper> {
  const response = await requestAPI<IAPIResponse<IPaper>>('library', {
    method: 'POST',
    body: JSON.stringify(paper)
  });

  return handleAPIResponse(response, 'Import failed');
}

export async function importPDF(
  file: File,
  aiConfig?: {
    enabled?: boolean;
    provider?: string;
    apiKey?: string;
    model?: string;
    ollamaUrl?: string;
  }
): Promise<IPaper> {
  const formData = new FormData();
  formData.append('file', file);
  if (aiConfig) {
    // Append as a file-like object so backend can read it from request.files
    const aiConfigBlob = new Blob([JSON.stringify(aiConfig)], {
      type: 'application/json'
    });
    formData.append('aiConfig', aiConfigBlob, 'aiConfig.json');
  }

  const response = await requestAPI<IAPIResponse<IPaper>>('import', {
    method: 'POST',
    body: formData
  });

  return handleAPIResponse(response, 'PDF import failed');
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
