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
  open_access_pdf?: string;
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
  limit: number = 20,
  offset: number = 0
): Promise<IDiscoveryResponse> {
  return retryWithBackoff(async () => {
    const params = new URLSearchParams({ q: query });
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

export interface IImportPaperResponse {
  paper: IPaper;
  is_duplicate: boolean;
  already_has_pdf?: boolean;
}

export async function importPaper(
  paper: IPaper
): Promise<IImportPaperResponse> {
  const response = await requestAPI<IAPIResponse<IImportPaperResponse>>(
    'library',
    {
      method: 'POST',
      body: JSON.stringify(paper)
    }
  );

  const result = handleAPIResponse(response, 'Import failed');
  return result;
}

export async function deletePapers(
  paperIds: number[]
): Promise<{ deleted_count: number }> {
  const response = await requestAPI<IAPIResponse<{ deleted_count: number }>>(
    'library',
    {
      method: 'DELETE',
      body: JSON.stringify({ paper_ids: paperIds })
    }
  );

  return handleAPIResponse(response, 'Delete failed') || { deleted_count: 0 };
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
): Promise<IImportPaperResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (aiConfig) {
    // Append as a file-like object so backend can read it from request.files
    const aiConfigBlob = new Blob([JSON.stringify(aiConfig)], {
      type: 'application/json'
    });
    formData.append('aiConfig', aiConfigBlob, 'aiConfig.json');
  }

  const response = await requestAPI<IAPIResponse<IImportPaperResponse>>(
    'import',
    {
      method: 'POST',
      body: formData
    }
  );

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
  const { downloadBlob } = await import('./utils/download');
  downloadBlob(blob, `library.${format === 'bibtex' ? 'bib' : format}`);
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

  return handleAPIResponse(response, 'WWC assessment failed');
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

  return handleAPIResponse(response, 'Meta-analysis failed');
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
  status?: 'success' | 'disabled';
  message?: string;
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

  return handleAPIResponse(response, 'Conflict detection failed');
}

// Subgroup Analysis Types and Functions
export interface ISubgroupComparison {
  q_between: number | null;
  df: number | null;
  p_value: number | null;
  interpretation: string;
}

export interface ISubgroupAnalysisResult {
  subgroups: Record<string, IMetaAnalysisResult>;
  overall: IMetaAnalysisResult;
  subgroup_variable: string;
  n_subgroups: number;
  subgroup_comparison: ISubgroupComparison;
}

export async function performSubgroupAnalysis(
  paperIds: number[],
  subgroupVariable: string,
  outcomeName?: string
): Promise<ISubgroupAnalysisResult> {
  const response = await requestAPI<IAPIResponse<ISubgroupAnalysisResult>>(
    'subgroup-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        subgroup_variable: subgroupVariable,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Subgroup analysis failed');
  }

  if (!response.data) {
    throw new Error('No subgroup analysis data returned');
  }

  return response.data;
}

// Publication Bias Assessment Types and Functions
export interface IBiasAssessmentResult {
  eggers_test: {
    intercept: number | null;
    intercept_se: number | null;
    intercept_pvalue: number | null;
    interpretation: string;
  };
  funnel_plot: string;
  n_studies: number;
}

export async function assessPublicationBias(
  paperIds: number[],
  outcomeName?: string
): Promise<IBiasAssessmentResult> {
  const response = await requestAPI<IAPIResponse<IBiasAssessmentResult>>(
    'bias-assessment',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Bias assessment failed');
  }

  if (!response.data) {
    throw new Error('No bias assessment data returned');
  }

  return response.data;
}

// Sensitivity Analysis Types and Functions
export interface ISensitivityAnalysisResult {
  overall_effect: number;
  leave_one_out: Array<{
    removed_study: string;
    removed_paper_id?: number;
    pooled_effect: number;
    ci_lower: number;
    ci_upper: number;
    difference_from_overall: number;
  }>;
  influence_diagnostics: Array<{
    study_label: string;
    paper_id?: number;
    influence_score: number;
    weight: number;
    effect_size: number;
  }>;
  n_studies: number;
}

export async function performSensitivityAnalysis(
  paperIds: number[],
  outcomeName?: string
): Promise<ISensitivityAnalysisResult> {
  const response = await requestAPI<IAPIResponse<ISensitivityAnalysisResult>>(
    'sensitivity-analysis',
    {
      method: 'POST',
      body: JSON.stringify({
        paper_ids: paperIds,
        outcome_name: outcomeName
      })
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'Sensitivity analysis failed');
  }

  if (!response.data) {
    throw new Error('No sensitivity analysis data returned');
  }

  return response.data;
}

// Enhanced Conflict Detection with Findings
export interface IConflictDetectionWithFindingsResult
  extends IConflictDetectionResult {
  findings?: Record<number, string[]>; // Extracted findings by paper ID
}

export async function detectConflictsWithFindings(
  paperIds: number[],
  confidenceThreshold: number = 0.8
): Promise<IConflictDetectionWithFindingsResult> {
  const response = await requestAPI<
    IAPIResponse<IConflictDetectionWithFindingsResult>
  >('conflict-detection', {
    method: 'POST',
    body: JSON.stringify({
      paper_ids: paperIds,
      confidence_threshold: confidenceThreshold,
      extract_findings: true
    })
  });

  return handleAPIResponse(response, 'Conflict detection failed');
}
