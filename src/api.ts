import { requestAPI } from './request';

// Type definitions matching backend responses
export interface Paper {
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

export interface DiscoveryResponse {
  data: Paper[];
  total: number;
}

export interface APIResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

// API functions
export async function getLibrary(): Promise<Paper[]> {
  const response = await requestAPI<APIResponse<Paper[]>>('library', {
    method: 'GET'
  });

  if (response.status === 'error') {
    throw new Error(response.message || 'Failed to fetch library');
  }

  return response.data || [];
}

export async function searchLibrary(query: string): Promise<Paper[]> {
  const response = await requestAPI<APIResponse<Paper[]>>(
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
): Promise<DiscoveryResponse> {
  const params = new URLSearchParams({ q: query });
  if (year) {
    params.append('year', year);
  }
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  const response = await requestAPI<APIResponse<DiscoveryResponse>>(
    `discovery?${params.toString()}`,
    { method: 'GET' }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Semantic Scholar search failed');
  }

  return response.data || { data: [], total: 0 };
}

export async function importPaper(paper: Paper): Promise<Paper> {
  const response = await requestAPI<APIResponse<Paper>>('library', {
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

export async function importPDF(file: File): Promise<Paper> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await requestAPI<APIResponse<Paper>>('import', {
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
