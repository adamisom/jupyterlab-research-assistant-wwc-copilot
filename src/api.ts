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

// WWC Assessment Types and Functions
export interface IWWCAssessment {
  paper_id?: number;
  paper_title?: string;
  chosen_attrition_boundary: string;
  adjustment_strategy_is_valid?: boolean;
  randomization_documented?: boolean;
  is_rct: boolean;
  overall_attrition?: number;
  differential_attrition?: number;
  is_high_attrition?: boolean;
  baseline_effect_size?: number;
  baseline_equivalence_satisfied?: boolean;
  final_rating: string;
  rating_justification: string[];
}

export interface IWWCAssessmentRequest {
  paper_id: number;
  judgments: {
    chosen_attrition_boundary?: 'cautious' | 'optimistic';
    adjustment_strategy_is_valid?: boolean;
    randomization_documented?: boolean;
  };
}

export async function runWWCAssessment(
  request: IWWCAssessmentRequest
): Promise<IWWCAssessment> {
  const response = await requestAPI<IAPIResponse<IWWCAssessment>>(
    'wwc-assessment',
    {
      method: 'POST',
      body: JSON.stringify(request)
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'WWC assessment failed');
  }

  if (!response.data) {
    throw new Error('No assessment data returned');
  }

  return response.data;
}

// Meta-Analysis Types and Functions
export interface IMetaAnalysisStudy {
  paper_id?: number;
  study_label: string;
  effect_size: number;
  std_error: number;
  weight: number;
  ci_lower: number;
  ci_upper: number;
}

export interface IMetaAnalysisResult {
  pooled_effect: number;
  ci_lower: number;
  ci_upper: number;
  p_value: number;
  tau_squared: number;
  i_squared: number;
  q_statistic: number;
  q_p_value: number;
  n_studies: number;
  studies: IMetaAnalysisStudy[];
  forest_plot?: string; // Base64-encoded image
  heterogeneity_interpretation?: string;
}

export async function performMetaAnalysis(
  paperIds: number[],
  outcomeName?: string
): Promise<IMetaAnalysisResult> {
  const response = await requestAPI<IAPIResponse<IMetaAnalysisResult>>(
    'meta-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Meta-analysis failed');
  }

  if (!response.data) {
    throw new Error('No meta-analysis data returned');
  }

  return response.data;
}

// Conflict Detection Types and Functions
export interface IConflictDetectionResult {
  contradictions: Array<{
    finding1: string;
    finding2: string;
    confidence: number;
    label: string;
    paper1_id?: number;
    paper1_title?: string;
    paper2_id?: number;
    paper2_title?: string;
  }>;
  n_papers: number;
  n_contradictions: number;
}

export async function detectConflicts(
  paperIds: number[],
  confidenceThreshold: number = 0.8
): Promise<IConflictDetectionResult> {
  const response = await requestAPI<IAPIResponse<IConflictDetectionResult>>(
    'conflict-detection',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        confidence_threshold: confidenceThreshold
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Conflict detection failed');
  }

  if (!response.data) {
    throw new Error('No conflict detection data returned');
  }

  return response.data;
}
