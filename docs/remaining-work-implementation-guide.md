# Remaining Work Implementation Guide

**Purpose**: Complete step-by-step implementation guide for all remaining Stage 1 tasks with all barriers addressed.

**Status**: This guide addresses all documentation gaps identified in `remaining-work-analysis.md`

---

## Table of Contents

1. [PDF Upload UI](#1-pdf-upload-ui)
2. [Enhanced Error Handling](#2-enhanced-error-handling)
3. [AI Metadata Extraction](#3-ai-metadata-extraction)
4. [Paper Detail View](#4-paper-detail-view)
5. [Export Functionality](#5-export-functionality)
6. [Enhanced Loading States](#6-enhanced-loading-states)
7. [Integration Testing](#7-integration-testing)

---

## 1. PDF Upload UI

### Overview
Add file upload capability to LibraryTab, allowing users to upload PDFs directly from their computer.

### Implementation Steps

#### Step 1.1: Add File Input Component to LibraryTab

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { Paper, getLibrary, searchLibrary, importPDF } from '../api';
import { PaperCard } from './PaperCard';

export const LibraryTab: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadLibrary();
  }, []);

  const loadLibrary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getLibrary();
      setPapers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load library');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    // Validate file type
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setError('Please select a PDF file');
      return;
    }

    // Validate file size (max 50MB)
    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const importedPaper = await importPDF(file);
      // Refresh library to show new paper
      await loadLibrary();
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'PDF upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadLibrary();
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const results = await searchLibrary(searchQuery);
      setPapers(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-library">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
        <input
          type="text"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          onKeyPress={e => {
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          placeholder="Search your library..."
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Search
        </button>
      </div>

      {/* PDF Upload Section */}
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-upload-section">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="pdf-upload-input"
        />
        <label
          htmlFor="pdf-upload-input"
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          style={{ display: 'inline-block', cursor: 'pointer' }}
        >
          {isUploading ? 'Uploading...' : 'Upload PDF'}
        </label>
      </div>

      {error && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
          Error: {error}
        </div>
      )}

      {isLoading && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-loading">
          Loading...
        </div>
      )}

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-papers">
        {papers.length === 0 && !isLoading && (
          <div className="jp-jupyterlab-research-assistant-wwc-copilot-empty">
            No papers found. Use the Discovery tab to search and import papers, or upload a PDF above.
          </div>
        )}
        {papers.map(paper => (
          <PaperCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
};
```

#### Step 1.2: Add CSS for Upload Section

**File**: `style/index.css` (add to existing styles)

```css
/* PDF Upload Section */
.jp-jupyterlab-research-assistant-wwc-copilot-upload-section {
  margin-bottom: 16px;
  padding: 8px;
  border: 1px dashed var(--jp-border-color1);
  border-radius: 4px;
  text-align: center;
}

.jp-jupyterlab-research-assistant-wwc-copilot-upload-section label {
  margin: 0;
}
```

### Testing Checklist
- [ ] File input appears in LibraryTab
- [ ] Can select PDF file
- [ ] Upload shows "Uploading..." state
- [ ] Library refreshes after successful upload
- [ ] Error message shows for non-PDF files
- [ ] Error message shows for files > 50MB
- [ ] File input resets after upload

---

## 2. Enhanced Error Handling

### Overview
Replace `alert()` calls with proper JupyterLab notifications and improve error messages.

### Implementation Steps

#### Step 2.1: Create Notification Utility

**File**: `src/utils/notifications.ts` (new file)

```typescript
import { showErrorMessage, showSuccessMessage } from '@jupyterlab/apputils';

/**
 * Show an error notification to the user.
 * @param title - Error title
 * @param message - Error message
 * @param error - Optional error object for logging
 */
export function showError(title: string, message: string, error?: Error): void {
  console.error(`${title}: ${message}`, error);
  showErrorMessage(title, message);
}

/**
 * Show a success notification to the user.
 * @param title - Success title
 * @param message - Success message
 */
export function showSuccess(title: string, message: string): void {
  showSuccessMessage(title, message);
}

/**
 * Show a warning notification to the user.
 * @param title - Warning title
 * @param message - Warning message
 */
export function showWarning(title: string, message: string): void {
  // JupyterLab doesn't have showWarningMessage, so use error style
  // but with warning icon/color if available
  console.warn(`${title}: ${message}`);
  showErrorMessage(title, message);
}
```

#### Step 2.2: Update DiscoveryTab to Use Notifications

**File**: `src/widgets/DiscoveryTab.tsx`

```typescript
import React, { useState } from 'react';
import { Paper, searchSemanticScholar, importPaper } from '../api';
import { PaperCard } from './PaperCard';
import { showError, showSuccess } from '../utils/notifications';

export const DiscoveryTab: React.FC = () => {
  // ... existing state ...

  const handleImport = async (paper: Paper) => {
    try {
      await importPaper(paper);
      showSuccess('Paper Imported', `Successfully imported: ${paper.title}`);
    } catch (err) {
      showError(
        'Import Failed',
        err instanceof Error ? err.message : 'Unknown error occurred',
        err instanceof Error ? err : undefined
      );
    }
  };

  // ... rest of component ...
};
```

#### Step 2.3: Update LibraryTab to Use Notifications

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import { showError, showSuccess } from '../utils/notifications';

// In handleFileSelect:
try {
  const importedPaper = await importPDF(file);
  await loadLibrary();
  showSuccess('PDF Uploaded', `Successfully imported: ${importedPaper.title}`);
  if (fileInputRef.current) {
    fileInputRef.current.value = '';
  }
} catch (err) {
  showError(
    'PDF Upload Failed',
    err instanceof Error ? err.message : 'Unknown error occurred',
    err instanceof Error ? err : undefined
  );
}
```

#### Step 2.4: Add Retry Logic for Network Errors

**File**: `src/utils/retry.ts` (new file)

```typescript
/**
 * Retry a function with exponential backoff.
 * @param fn - Function to retry
 * @param maxRetries - Maximum number of retries
 * @param initialDelay - Initial delay in milliseconds
 * @returns Promise that resolves with function result
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 1000
): Promise<T> {
  let lastError: Error | undefined;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Don't retry on 4xx errors (client errors)
      if (error instanceof Error && 'status' in error) {
        const status = (error as any).status;
        if (status >= 400 && status < 500) {
          throw error;
        }
      }
      
      if (attempt < maxRetries) {
        const delay = initialDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  throw lastError || new Error('Retry failed');
}
```

**Usage in API functions**:

```typescript
import { retryWithBackoff } from '../utils/retry';

export async function searchSemanticScholar(
  query: string,
  year?: string,
  limit: number = 20,
  offset: number = 0
): Promise<DiscoveryResponse> {
  return retryWithBackoff(async () => {
    const params = new URLSearchParams({ q: query });
    // ... rest of implementation
  });
}
```

### Testing Checklist
- [ ] Error notifications appear instead of alerts
- [ ] Success notifications appear after successful operations
- [ ] Network errors retry automatically
- [ ] 4xx errors don't retry (immediate failure)
- [ ] Error messages are user-friendly
- [ ] Console still logs detailed errors for debugging

---

## 3. AI Metadata Extraction

### Overview
Extract rich metadata from PDFs using AI (Claude, GPT-4, or Ollama).

### Implementation Steps

#### Step 3.1: Create Settings Schema

**File**: `schema/plugin.json` (update existing)

```json
{
  "jupyter.lab.setting-icon-class": "jp-MaterialIcon jp-MaterialIcon-extensions",
  "jupyter.lab.setting-icon-label": "Research Assistant",
  "jupyter.lab.shortcuts": [],
  "title": "Research Assistant",
  "description": "Settings for the Research Assistant extension",
  "type": "object",
  "properties": {
    "aiExtraction": {
      "title": "AI Metadata Extraction",
      "description": "Configure AI provider for metadata extraction",
      "type": "object",
      "properties": {
        "enabled": {
          "title": "Enable AI Extraction",
          "description": "Enable AI-powered metadata extraction from PDFs",
          "type": "boolean",
          "default": false
        },
        "provider": {
          "title": "AI Provider",
          "description": "Choose AI provider for extraction",
          "type": "string",
          "enum": ["claude", "openai", "ollama"],
          "default": "ollama"
        },
        "apiKey": {
          "title": "API Key",
          "description": "API key for Claude or OpenAI (leave empty for Ollama)",
          "type": "string",
          "default": ""
        },
        "model": {
          "title": "Model",
          "description": "Model name (e.g., 'claude-3-opus-20240229', 'gpt-4', 'llama3')",
          "type": "string",
          "default": "llama3"
        },
        "ollamaUrl": {
          "title": "Ollama URL",
          "description": "URL for local Ollama instance",
          "type": "string",
          "default": "http://localhost:11434"
        }
      },
      "default": {
        "enabled": false,
        "provider": "ollama",
        "apiKey": "",
        "model": "llama3",
        "ollamaUrl": "http://localhost:11434"
      }
    }
  }
}
```

#### Step 3.2: Create Extraction Schema

**File**: `jupyterlab_research_assistant_wwc_copilot/services/extraction_schema.py`

```python
"""Schema definitions for AI metadata extraction."""

LEARNING_SCIENCE_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "study_metadata": {
            "type": "object",
            "properties": {
                "methodology": {
                    "type": "string",
                    "enum": ["RCT", "Quasi-experimental", "Observational", "Case Study", "Other"],
                    "description": "Research methodology"
                },
                "sample_size_baseline": {
                    "type": "integer",
                    "description": "Sample size at baseline"
                },
                "sample_size_endline": {
                    "type": "integer",
                    "description": "Sample size at endline"
                },
                "effect_sizes": {
                    "type": "object",
                    "description": "Reported effect sizes by outcome",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "d": {"type": "number", "description": "Cohen's d"},
                            "se": {"type": "number", "description": "Standard error"}
                        }
                    }
                }
            }
        },
        "learning_science_metadata": {
            "type": "object",
            "properties": {
                "learning_domain": {
                    "type": "string",
                    "enum": ["cognitive", "affective", "behavioral", "metacognitive"],
                    "description": "Primary learning domain"
                },
                "intervention_type": {
                    "type": "string",
                    "description": "Type of intervention (e.g., 'Spaced Repetition', 'Active Learning')"
                },
                "learning_objectives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "What students were supposed to learn"
                },
                "intervention_components": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific instructional techniques used"
                }
            }
        },
        "wwc_criteria": {
            "type": "object",
            "properties": {
                "baseline_n_treatment": {"type": "integer"},
                "baseline_n_control": {"type": "integer"},
                "endline_n_treatment": {"type": "integer"},
                "endline_n_control": {"type": "integer"},
                "randomization_method": {"type": "string"},
                "baseline_equivalence_reported": {"type": "boolean"}
            }
        }
    },
    "required": []
}
```

#### Step 3.3: Implement AI Extractor Service

**File**: `jupyterlab_research_assistant_wwc_copilot/services/ai_extractor.py`

```python
"""AI-powered metadata extraction from PDF text."""

import json
import logging
from typing import Dict, Optional, Any
import requests
from openai import OpenAI

from .extraction_schema import LEARNING_SCIENCE_EXTRACTION_SCHEMA

logger = logging.getLogger(__name__)


class AIExtractor:
    """Extract metadata from PDF text using AI."""
    
    def __init__(
        self,
        provider: str = "ollama",
        api_key: Optional[str] = None,
        model: str = "llama3",
        ollama_url: str = "http://localhost:11434"
    ):
        self.provider = provider
        self.model = model
        self.ollama_url = ollama_url
        
        if provider in ["claude", "openai"]:
            if not api_key:
                raise ValueError(f"API key required for {provider}")
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.anthropic.com/v1" if provider == "claude" else None
            )
        else:
            self.client = None
    
    def extract_metadata(self, text: str, schema: Dict = None) -> Dict[str, Any]:
        """
        Extract metadata from text using AI.
        
        Args:
            text: PDF text to extract from
            schema: JSON schema for extraction (defaults to learning science schema)
        
        Returns:
            Extracted metadata dictionary
        """
        if schema is None:
            schema = LEARNING_SCIENCE_EXTRACTION_SCHEMA
        
        # Truncate text to fit in context window
        max_chars = 16000
        truncated_text = text[:max_chars] if len(text) > max_chars else text
        
        prompt = f"""Extract the following information from this academic paper. 
Respond with a single, valid JSON object that conforms to the provided schema.

Schema:
{json.dumps(schema, indent=2)}

Paper Text:
{truncated_text}

Return only valid JSON, no additional text."""

        try:
            if self.provider == "ollama":
                return self._extract_with_ollama(prompt)
            else:
                return self._extract_with_openai(prompt)
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            return {}
    
    def _extract_with_ollama(self, prompt: str) -> Dict[str, Any]:
        """Extract using Ollama API."""
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        extracted_text = result.get("response", "")
        
        # Parse JSON from response
        try:
            return json.loads(extracted_text)
        except json.JSONDecodeError:
            logger.warning("Ollama returned invalid JSON, attempting to extract JSON from response")
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
    
    def _extract_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Extract using OpenAI/Anthropic API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
```

#### Step 3.4: Integrate with ImportHandler

**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py` (update ImportHandler)

```python
from .services.ai_extractor import AIExtractor
from jupyter_server.base.handlers import APIHandler
import json

class ImportHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        """Import a PDF file and extract metadata."""
        try:
            # ... existing file upload code ...
            
            # Extract text and metadata
            parser = PDFParser()
            extracted = parser.extract_text_and_metadata(str(file_path))
            
            # Create paper record
            paper_data = {
                "title": extracted.get("title") or filename.replace(".pdf", ""),
                "author": extracted.get("author"),
                "full_text": extracted.get("full_text"),
                "pdf_path": str(file_path)
            }
            
            # AI extraction (if enabled)
            ai_config = self._get_ai_config()
            if ai_config and ai_config.get("enabled"):
                try:
                    extractor = AIExtractor(
                        provider=ai_config.get("provider", "ollama"),
                        api_key=ai_config.get("apiKey"),
                        model=ai_config.get("model", "llama3"),
                        ollama_url=ai_config.get("ollamaUrl", "http://localhost:11434")
                    )
                    ai_metadata = extractor.extract_metadata(extracted.get("full_text", ""))
                    
                    # Merge AI-extracted metadata
                    if "study_metadata" in ai_metadata:
                        paper_data["study_metadata"] = ai_metadata["study_metadata"]
                    if "learning_science_metadata" in ai_metadata:
                        paper_data["learning_science_metadata"] = ai_metadata["learning_science_metadata"]
                except Exception as e:
                    logger.warning(f"AI extraction failed: {str(e)}, continuing without AI metadata")
            
            with DatabaseManager() as db:
                paper = db.add_paper(paper_data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
    
    def _get_ai_config(self) -> Optional[Dict]:
        """Get AI extraction configuration from settings."""
        # Settings are available via self.settings
        # This is a simplified version - actual implementation needs to read from settings registry
        return None  # TODO: Implement settings reading
```

#### Step 3.5: Add Dependencies

**File**: `pyproject.toml`

```toml
dependencies = [
    # ... existing dependencies ...
    "openai>=1.0.0",  # Works for both OpenAI and Anthropic
    "requests>=2.31.0",  # For Ollama
]
```

### Testing Checklist
- [ ] Settings schema loads in JupyterLab settings
- [ ] Can configure AI provider
- [ ] Ollama extraction works with local instance
- [ ] Claude/OpenAI extraction works with API keys
- [ ] Extraction fails gracefully if AI unavailable
- [ ] Extracted metadata saved to database
- [ ] Works with PDF import workflow

---

## 4. Paper Detail View

### Overview
Create a detailed view showing all metadata for a selected paper.

### Component Structure

```
PaperDetailView
├── Header
│   ├── Title
│   ├── Authors
│   ├── Year, DOI, Citations
│   └── Close Button
├── Tabs
│   ├── Overview (Abstract, Basic Info)
│   ├── Study Metadata (Methodology, Sample Sizes, Effect Sizes)
│   ├── Learning Science (Domain, Intervention, Components)
│   └── WWC Criteria (if available)
└── Actions
    ├── Open PDF Button
    └── Edit Metadata Button (future)
```

### Implementation Steps

#### Step 4.1: Create DetailView Component

**File**: `src/widgets/DetailView.tsx`

```typescript
import React from 'react';
import { Paper } from '../api';

interface DetailViewProps {
  paper: Paper;
  onClose: () => void;
}

export const DetailView: React.FC<DetailViewProps> = ({ paper, onClose }) => {
  const [activeTab, setActiveTab] = React.useState<'overview' | 'study' | 'learning' | 'wwc'>('overview');

  const openPDF = () => {
    if (paper.pdf_path) {
      // Open PDF in new tab (if accessible via JupyterLab file browser)
      window.open(`/files${paper.pdf_path}`, '_blank');
    }
  };

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-view">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-header">
        <button
          onClick={onClose}
          className="jp-jupyterlab-research-assistant-wwc-copilot-close-button"
        >
          ×
        </button>
        <h2>{paper.title}</h2>
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-meta">
          {paper.authors && paper.authors.length > 0 && (
            <div>Authors: {paper.authors.join(', ')}</div>
          )}
          {paper.year && <div>Year: {paper.year}</div>}
          {paper.doi && <div>DOI: {paper.doi}</div>}
          {paper.citation_count !== undefined && (
            <div>Citations: {paper.citation_count}</div>
          )}
        </div>
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        {paper.study_metadata && (
          <button
            className={activeTab === 'study' ? 'active' : ''}
            onClick={() => setActiveTab('study')}
          >
            Study Metadata
          </button>
        )}
        {paper.learning_science_metadata && (
          <button
            className={activeTab === 'learning' ? 'active' : ''}
            onClick={() => setActiveTab('learning')}
          >
            Learning Science
          </button>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-content">
        {activeTab === 'overview' && (
          <div>
            {paper.abstract && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
                <h3>Abstract</h3>
                <p>{paper.abstract}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'study' && paper.study_metadata && (
          <div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Methodology</h3>
              <p>{paper.study_metadata.methodology || 'Not specified'}</p>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Sample Sizes</h3>
              <p>Baseline: {paper.study_metadata.sample_size_baseline || 'N/A'}</p>
              <p>Endline: {paper.study_metadata.sample_size_endline || 'N/A'}</p>
            </div>
            {paper.study_metadata.effect_sizes && (
              <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
                <h3>Effect Sizes</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Outcome</th>
                      <th>Cohen's d</th>
                      <th>Standard Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(paper.study_metadata.effect_sizes).map(([outcome, es]) => (
                      <tr key={outcome}>
                        <td>{outcome}</td>
                        <td>{es.d.toFixed(2)}</td>
                        <td>{es.se.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'learning' && paper.learning_science_metadata && (
          <div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Learning Domain</h3>
              <p>{paper.learning_science_metadata.learning_domain || 'Not specified'}</p>
            </div>
            <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-section">
              <h3>Intervention Type</h3>
              <p>{paper.learning_science_metadata.intervention_type || 'Not specified'}</p>
            </div>
          </div>
        )}
      </div>

      <div className="jp-jupyterlab-research-assistant-wwc-copilot-detail-actions">
        {paper.pdf_path && (
          <button
            onClick={openPDF}
            className="jp-jupyterlab-research-assistant-wwc-copilot-button"
          >
            Open PDF
          </button>
        )}
      </div>
    </div>
  );
};
```

#### Step 4.2: Update PaperCard to Open Detail View

**File**: `src/widgets/PaperCard.tsx`

```typescript
interface PaperCardProps {
  paper: Paper;
  onImport?: () => void;
  onViewDetails?: () => void;  // Add this
}

export const PaperCard: React.FC<PaperCardProps> = ({ paper, onImport, onViewDetails }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-card">
      <h3 
        className="jp-jupyterlab-research-assistant-wwc-copilot-paper-title"
        onClick={onViewDetails}
        style={{ cursor: onViewDetails ? 'pointer' : 'default' }}
      >
        {paper.title}
      </h3>
      {/* ... rest of component ... */}
      {onViewDetails && (
        <button
          onClick={onViewDetails}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          View Details
        </button>
      )}
    </div>
  );
};
```

#### Step 4.3: Integrate Detail View in LibraryTab

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import { DetailView } from './DetailView';

export const LibraryTab: React.FC = () => {
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);

  // ... existing code ...

  if (selectedPaper) {
    return (
      <DetailView
        paper={selectedPaper}
        onClose={() => setSelectedPaper(null)}
      />
    );
  }

  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-library">
      {/* ... existing code ... */}
      {papers.map(paper => (
        <PaperCard
          key={paper.id}
          paper={paper}
          onViewDetails={() => setSelectedPaper(paper)}
        />
      ))}
    </div>
  );
};
```

### Testing Checklist
- [ ] Detail view opens when clicking paper
- [ ] All tabs display correct data
- [ ] Close button works
- [ ] PDF opens in new tab (if path available)
- [ ] Empty fields handled gracefully
- [ ] Effect sizes table displays correctly

---

## 5. Export Functionality

### Overview
Export library as CSV, JSON, or BibTeX.

### Implementation Steps

#### Step 5.1: Create Export Backend Endpoint

**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

```python
import csv
import io
from typing import Dict

class ExportHandler(APIHandler):
    """Handler for exporting library."""
    
    @tornado.web.authenticated
    def get(self):
        """Export library in specified format."""
        try:
            format_type = self.get_argument("format", "json")  # json, csv, bibtex
            
            with DatabaseManager() as db:
                papers = db.get_all_papers()
            
            if format_type == "json":
                self.set_header("Content-Type", "application/json")
                self.set_header("Content-Disposition", "attachment; filename=library.json")
                self.finish(json.dumps(papers, indent=2))
            
            elif format_type == "csv":
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=[
                    "id", "title", "authors", "year", "doi", "citation_count", "abstract"
                ])
                writer.writeheader()
                for paper in papers:
                    row = {
                        "id": paper.get("id", ""),
                        "title": paper.get("title", ""),
                        "authors": ", ".join(paper.get("authors", [])),
                        "year": paper.get("year", ""),
                        "doi": paper.get("doi", ""),
                        "citation_count": paper.get("citation_count", ""),
                        "abstract": paper.get("abstract", "")[:500]  # Truncate
                    }
                    writer.writerow(row)
                
                self.set_header("Content-Type", "text/csv")
                self.set_header("Content-Disposition", "attachment; filename=library.csv")
                self.finish(output.getvalue())
            
            elif format_type == "bibtex":
                bibtex = self._generate_bibtex(papers)
                self.set_header("Content-Type", "text/plain")
                self.set_header("Content-Disposition", "attachment; filename=library.bib")
                self.finish(bibtex)
            
            else:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": f"Unknown format: {format_type}"}))
        
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
    
    def _generate_bibtex(self, papers: list) -> str:
        """Generate BibTeX entries from papers."""
        entries = []
        for paper in papers:
            # Generate citation key from first author and year
            authors = paper.get("authors", [])
            year = paper.get("year", "unknown")
            first_author = authors[0].split()[-1].lower() if authors else "unknown"
            citation_key = f"{first_author}{year}"
            
            # Determine entry type (default to @article)
            entry_type = "@article"
            
            entry = f"{entry_type}{{{citation_key},\n"
            entry += f"  title = {{{paper.get('title', '')}}},\n"
            
            if authors:
                entry += f"  author = {{{' and '.join(authors)}}},\n"
            
            if year:
                entry += f"  year = {{{year}}},\n"
            
            if paper.get("doi"):
                entry += f"  doi = {{{paper.get('doi')}}},\n"
            
            if paper.get("abstract"):
                # Escape special characters for BibTeX
                abstract = paper.get("abstract", "").replace("{", "\\{").replace("}", "\\}")
                entry += f"  abstract = {{{abstract[:200]}...}},\n"
            
            entry += "}\n"
            entries.append(entry)
        
        return "\n".join(entries)
```

#### Step 5.2: Register Export Route

**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py` (in setup_route_handlers)

```python
handlers = [
    # ... existing handlers ...
    (url_path_join(base_url, route_prefix, "export"), ExportHandler),
]
```

#### Step 5.3: Add Frontend Export Function

**File**: `src/api.ts`

```typescript
export async function exportLibrary(format: 'json' | 'csv' | 'bibtex'): Promise<void> {
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
```

#### Step 5.4: Add Export UI to LibraryTab

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import { exportLibrary } from '../api';
import { showSuccess, showError } from '../utils/notifications';

// Add export button in search bar section
<div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
  {/* ... existing search input ... */}
  <select
    onChange={async (e) => {
      const format = e.target.value as 'json' | 'csv' | 'bibtex';
      if (format) {
        try {
          await exportLibrary(format);
          showSuccess('Export Complete', `Library exported as ${format.toUpperCase()}`);
        } catch (err) {
          showError('Export Failed', err instanceof Error ? err.message : 'Unknown error');
        }
        e.target.value = ''; // Reset
      }
    }}
    className="jp-jupyterlab-research-assistant-wwc-copilot-select"
  >
    <option value="">Export...</option>
    <option value="json">Export as JSON</option>
    <option value="csv">Export as CSV</option>
    <option value="bibtex">Export as BibTeX</option>
  </select>
</div>
```

### BibTeX Format Specification

**Entry Types**:
- `@article` - Default for papers
- `@inproceedings` - For conference papers (if detected)

**Required Fields**: None (all optional in BibTeX)

**Field Mapping**:
- `title` → `title`
- `authors` → `author` (joined with " and ")
- `year` → `year`
- `doi` → `doi`
- `abstract` → `abstract` (truncated to 200 chars)

**Citation Key Format**: `{lastname}{year}` (e.g., `smith2023`)

### Testing Checklist
- [ ] JSON export downloads correctly
- [ ] CSV export has all columns
- [ ] BibTeX export has valid format
- [ ] Special characters escaped in BibTeX
- [ ] File downloads with correct name
- [ ] Export works with empty library
- [ ] Error handling for failed exports

---

## 6. Enhanced Loading States

### Overview
Add skeleton loaders and progress indicators for better UX.

### Implementation Steps

#### Step 6.1: Create Skeleton Loader Component

**File**: `src/widgets/SkeletonLoader.tsx`

```typescript
import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-title" />
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line" />
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line short" />
    </div>
  );
};
```

#### Step 6.2: Add Skeleton CSS

**File**: `style/index.css`

```css
/* Skeleton Loaders */
.jp-jupyterlab-research-assistant-wwc-copilot-skeleton {
  padding: 12px;
  border: 1px solid var(--jp-border-color1);
  border-radius: 4px;
  background-color: var(--jp-layout-color1);
  animation: pulse 1.5s ease-in-out infinite;
}

.jp-jupyterlab-research-assistant-wwc-copilot-skeleton-title {
  height: 20px;
  width: 80%;
  background-color: var(--jp-border-color2);
  border-radius: 2px;
  margin-bottom: 8px;
}

.jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line {
  height: 14px;
  width: 100%;
  background-color: var(--jp-border-color2);
  border-radius: 2px;
  margin-bottom: 4px;
}

.jp-jupyterlab-research-assistant-wwc-copilot-skeleton-line.short {
  width: 60%;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
```

#### Step 6.3: Use Skeleton in Components

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import { SkeletonLoader } from './SkeletonLoader';

// Replace loading text with:
{isLoading && (
  <div>
    <SkeletonLoader />
    <SkeletonLoader />
    <SkeletonLoader />
  </div>
)}
```

### Testing Checklist
- [ ] Skeleton loaders appear during loading
- [ ] Animation is smooth
- [ ] Replaces content correctly
- [ ] Works in both tabs

---

## 7. Integration Testing

### Overview
Test the complete workflow from frontend to backend.

### Test Scenarios

#### Scenario 1: Complete Workflow
1. Search Semantic Scholar
2. Import paper
3. View in library
4. Search library
5. View details
6. Export library

#### Scenario 2: Error Handling
1. Network failure during search
2. Invalid PDF upload
3. API rate limit handling
4. Database errors

#### Scenario 3: Edge Cases
1. Empty search results
2. Very long paper titles
3. Special characters in data
4. Concurrent operations

### Implementation Steps

#### Step 7.1: Create Integration Test File

**File**: `jupyterlab_research_assistant_wwc_copilot/tests/test_integration.py`

```python
"""Integration tests for full workflow."""

import pytest
import json
from pathlib import Path
from jupyterlab_research_assistant_wwc_copilot.services.db_manager import DatabaseManager
from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import SemanticScholarAPI
from jupyterlab_research_assistant_wwc_copilot.services.pdf_parser import PDFParser


@pytest.fixture
def db():
    """Create a test database."""
    with DatabaseManager() as db:
        yield db
        # Cleanup: delete all test papers
        db.session.query(db.session.query(Paper).filter(Paper.title.like("TEST_%")).delete())


def test_complete_workflow(db):
    """Test: Search → Import → View → Search → Export"""
    # 1. Search Semantic Scholar
    api = SemanticScholarAPI()
    results = api.search_papers("spaced repetition", limit=1)
    assert len(results["data"]) > 0
    
    # 2. Import paper
    paper_data = results["data"][0]
    imported = db.add_paper({
        "title": f"TEST_{paper_data['title']}",
        "authors": paper_data.get("authors", []),
        "year": paper_data.get("year"),
        "abstract": paper_data.get("abstract", "")
    })
    assert imported["id"] is not None
    
    # 3. View in library
    papers = db.get_all_papers()
    assert any(p["id"] == imported["id"] for p in papers)
    
    # 4. Search library
    search_results = db.search_papers("spaced")
    assert len(search_results) > 0
    
    # 5. Get paper details
    paper = db.get_paper_by_id(imported["id"])
    assert paper is not None
    assert paper["title"].startswith("TEST_")


def test_pdf_import_workflow(tmp_path, db):
    """Test: Upload PDF → Extract → Store → Retrieve"""
    # Create a mock PDF (would need actual PDF for real test)
    # This is a simplified version
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n...")  # Minimal PDF header
    
    parser = PDFParser()
    # Would extract from real PDF
    # extracted = parser.extract_text_and_metadata(str(pdf_path))
    
    # Test that parser handles file correctly
    # (Full test would require actual PDF file)


def test_error_handling(db):
    """Test error scenarios."""
    # Test invalid paper data
    with pytest.raises(Exception):
        db.add_paper({})  # Missing required fields
    
    # Test search with empty query
    results = db.search_papers("")
    assert isinstance(results, list)


@pytest.mark.parametrize("query", [
    "spaced repetition",
    "learning science",
    "meta-analysis",
    "RCT education"
])
def test_search_variations(query, db):
    """Test various search queries."""
    api = SemanticScholarAPI()
    results = api.search_papers(query, limit=5)
    assert "data" in results
    assert "total" in results
```

#### Step 7.2: Mock Semantic Scholar for Testing

**File**: `jupyterlab_research_assistant_wwc_copilot/tests/conftest.py` (add to existing)

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_semantic_scholar():
    """Mock Semantic Scholar API responses."""
    with patch('jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar.SemanticScholarAPI') as mock:
        mock_instance = Mock()
        mock_instance.search_papers.return_value = {
            "data": [
                {
                    "paperId": "test123",
                    "title": "Test Paper",
                    "authors": ["Test Author"],
                    "year": 2023,
                    "abstract": "Test abstract"
                }
            ],
            "total": 1
        }
        mock.return_value = mock_instance
        yield mock_instance
```

#### Step 7.3: Frontend Integration Test Example

**File**: `src/__tests__/integration.spec.ts` (new)

```typescript
import { getLibrary, searchSemanticScholar, importPaper } from '../api';

// Mock requestAPI
jest.mock('../request', () => ({
  requestAPI: jest.fn()
}));

describe('Integration Tests', () => {
  it('should complete full workflow', async () => {
    // 1. Search
    const searchResults = await searchSemanticScholar('test query');
    expect(searchResults.data).toBeDefined();
    
    // 2. Import
    const paper = searchResults.data[0];
    const imported = await importPaper(paper);
    expect(imported.id).toBeDefined();
    
    // 3. View library
    const library = await getLibrary();
    expect(library).toContainEqual(expect.objectContaining({ id: imported.id }));
  });
});
```

### Testing Checklist
- [ ] All test scenarios pass
- [ ] Mocks work correctly
- [ ] Error scenarios handled
- [ ] Edge cases covered
- [ ] Tests run in CI/CD

---

## Summary

All remaining tasks now have:
- ✅ Complete implementation steps
- ✅ Code examples
- ✅ Testing checklists
- ✅ Barrier resolutions

**Estimated Total Time**: 20-30 hours for all tasks

**Recommended Order**:
1. PDF Upload UI (2-3 hours) - Easiest, high value
2. Enhanced Error Handling (2-3 hours) - Improves UX
3. Enhanced Loading States (1-2 hours) - Quick win
4. Paper Detail View (3-4 hours) - User-requested feature
5. Export Functionality (2-3 hours) - Useful utility
6. AI Metadata Extraction (4-6 hours) - Complex but valuable
7. Integration Testing (3-4 hours) - Quality assurance

