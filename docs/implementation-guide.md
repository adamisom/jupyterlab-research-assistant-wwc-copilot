# WWC Co-Pilot Implementation Guide

**Purpose**: Step-by-step implementation guide for rapid iteration with manual testing checkpoints.

**⚠️ Note**: This guide currently covers **Stage 1: Research Library** only. Stage 2 (WWC Co-Pilot & Synthesis Engine) will be added in a future update.

**Project Name**: `jupyterlab-research-assistant-wwc-copilot`  
**Python Package**: `jupyterlab_research_assistant_wwc_copilot`  
**Plugin ID**: `jupyterlab-research-assistant-wwc-copilot:plugin`  
**API Route Prefix**: `/jupyterlab-research-assistant-wwc-copilot`

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Development Workflow](#development-workflow)
3. [Stage 1: Research Library - Backend](#stage-1-research-library-backend)
4. [Stage 1: Research Library - Frontend](#stage-1-research-library-frontend)
5. [Stage 2: WWC Co-Pilot - Backend](#stage-2-wwc-co-pilot-backend)
6. [Stage 2: WWC Co-Pilot - Frontend](#stage-2-wwc-co-pilot-frontend)
7. [Testing Checkpoints](#testing-checkpoints)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Project Structure

### Actual Directory Layout

```
jupyterlab-research-assistant-wwc-copilot/
├── jupyterlab_research_assistant_wwc_copilot/  # Python package (underscores)
│   ├── __init__.py                              # Server extension entry point
│   ├── routes.py                                # API handlers
│   ├── services/                                # Business logic
│   │   ├── __init__.py
│   │   ├── semantic_scholar.py                  # Semantic Scholar API client
│   │   ├── pdf_parser.py                        # PDF text extraction
│   │   ├── ai_extractor.py                     # AI metadata extraction
│   │   ├── db_manager.py                       # Database operations
│   │   └── wwc_assessor.py                     # WWC quality assessment
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                            # SQLAlchemy models
│   │   └── migrations/                          # Alembic migrations
│   └── tests/
│       ├── __init__.py
│       ├── test_routes.py
│       └── test_services.py
├── src/                                         # TypeScript frontend
│   ├── index.ts                                 # Plugin entry point
│   ├── request.ts                               # API client helper
│   ├── api.ts                                   # Typed API functions
│   ├── widgets/                                 # React components
│   │   ├── ResearchLibraryPanel.tsx
│   │   ├── DiscoveryTab.tsx
│   │   ├── LibraryTab.tsx
│   │   └── PaperCard.tsx
│   ├── commands.ts                              # Command definitions
│   └── __tests__/
├── schema/
│   └── plugin.json                              # Settings schema
└── docs/
```

### Key Naming Conventions

- **Python package**: `jupyterlab_research_assistant_wwc_copilot` (underscores, lowercase)
- **NPM package**: `jupyterlab-research-assistant-wwc-copilot` (dashes, lowercase)
- **Plugin ID**: `jupyterlab-research-assistant-wwc-copilot:plugin` (dashes, colon separator)
- **Command IDs**: `jupyterlab-research-assistant-wwc-copilot:command-name`
- **API Routes**: `/jupyterlab-research-assistant-wwc-copilot/endpoint-name`
- **CSS Classes**: `.jp-jupyterlab-research-assistant-wwc-copilot-ClassName`

---

## Development Workflow

### Initial Setup (One-Time)

```bash
# 1. Activate your environment
conda activate <your-env>  # or: source venv/bin/activate

# 2. Install in development mode
pip install -e ".[dev,test]"
jupyter labextension develop . --overwrite
jupyter server extension enable jupyterlab_research_assistant_wwc_copilot

# 3. Verify installation
jupyter labextension list  # Should show extension as "enabled" and "OK"
jupyter server extension list  # Should show backend extension
```

### Rapid Iteration Cycle

**For TypeScript/Frontend changes:**
```bash
# Terminal 1: Watch mode (auto-rebuilds on save)
jlpm watch

# Terminal 2: Run JupyterLab
jupyter lab

# After saving TypeScript files: Just refresh browser (Cmd+R / Ctrl+R)
```

**For Python/Backend changes:**
```bash
# Make your changes, then restart JupyterLab
# Press Ctrl+C in terminal, then:
jupyter lab
```

**Manual Testing Checkpoint:**
- After each feature: Test in browser, check console for errors
- After each API endpoint: Test with curl or browser dev tools
- After each UI component: Verify it renders and responds to interactions

---

## Stage 1: Research Library - Backend

### Phase 1.1: Database Setup

**File**: `jupyterlab_research_assistant_wwc_copilot/database/models.py`

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from pathlib import Path

Base = declarative_base()

class Paper(Base):
    __tablename__ = 'papers'
    
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    authors = Column(JSON)  # List of author names
    year = Column(Integer)
    doi = Column(String(255))
    s2_id = Column(String(255))  # Semantic Scholar ID
    citation_count = Column(Integer, default=0)
    pdf_path = Column(Text)  # Filesystem path to PDF
    abstract = Column(Text)
    full_text = Column(Text)  # Extracted PDF text
    
    # Relationships
    study_metadata = relationship("StudyMetadata", back_populates="paper", uselist=False)
    learning_science_metadata = relationship("LearningScienceMetadata", back_populates="paper", uselist=False)

class StudyMetadata(Base):
    __tablename__ = 'study_metadata'
    
    paper_id = Column(Integer, ForeignKey('papers.id'), primary_key=True)
    methodology = Column(String(50))  # "RCT", "Quasi-experimental", etc.
    sample_size_baseline = Column(Integer)
    sample_size_endline = Column(Integer)
    effect_sizes = Column(JSON)  # {"outcome_name": {"d": 0.5, "se": 0.1}, ...}
    
    paper = relationship("Paper", back_populates="study_metadata")

class LearningScienceMetadata(Base):
    __tablename__ = 'learning_science_metadata'
    
    paper_id = Column(Integer, ForeignKey('papers.id'), primary_key=True)
    learning_domain = Column(String(50))  # "cognitive", "affective", etc.
    intervention_type = Column(String(100))
    
    paper = relationship("Paper", back_populates="learning_science_metadata")

def get_db_path() -> Path:
    """Get the database file path in JupyterLab's data directory."""
    # Use JupyterLab's application data directory
    data_dir = Path.home() / ".jupyter" / "research_assistant"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "research_library.db"

def create_db_engine():
    """Create SQLAlchemy engine with database file."""
    db_path = get_db_path()
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_db_session():
    """Get a database session."""
    engine = create_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()
```

**File**: `jupyterlab_research_assistant_wwc_copilot/services/db_manager.py`

```python
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ..database.models import Paper, StudyMetadata, LearningScienceMetadata, get_db_session

class DatabaseManager:
    def __init__(self):
        self.session: Optional[Session] = None
    
    def __enter__(self):
        self.session = get_db_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is None:
                self.session.commit()
            else:
                self.session.rollback()
            self.session.close()
    
    def get_all_papers(self) -> List[Dict]:
        """Get all papers from database."""
        papers = self.session.query(Paper).all()
        return [self._paper_to_dict(p) for p in papers]
    
    def get_paper_by_id(self, paper_id: int) -> Optional[Dict]:
        """Get a single paper by ID."""
        paper = self.session.query(Paper).filter_by(id=paper_id).first()
        return self._paper_to_dict(paper) if paper else None
    
    def add_paper(self, data: Dict) -> Dict:
        """Add a new paper to the database."""
        paper = Paper(
            title=data.get('title', ''),
            authors=data.get('authors', []),
            year=data.get('year'),
            doi=data.get('doi'),
            s2_id=data.get('s2_id'),
            citation_count=data.get('citation_count', 0),
            pdf_path=data.get('pdf_path'),
            abstract=data.get('abstract'),
            full_text=data.get('full_text')
        )
        self.session.add(paper)
        self.session.flush()  # Get the ID
        
        # Add study metadata if provided
        if 'study_metadata' in data:
            study_meta = StudyMetadata(
                paper_id=paper.id,
                **data['study_metadata']
            )
            self.session.add(study_meta)
        
        # Add learning science metadata if provided
        if 'learning_science_metadata' in data:
            ls_meta = LearningScienceMetadata(
                paper_id=paper.id,
                **data['learning_science_metadata']
            )
            self.session.add(ls_meta)
        
        self.session.flush()
        return self._paper_to_dict(paper)
    
    def search_papers(self, query: str) -> List[Dict]:
        """Search papers by title, abstract, or authors."""
        papers = self.session.query(Paper).filter(
            (Paper.title.contains(query)) |
            (Paper.abstract.contains(query)) |
            (Paper.authors.contains(query))
        ).all()
        return [self._paper_to_dict(p) for p in papers]
    
    def _paper_to_dict(self, paper: Paper) -> Dict:
        """Convert Paper model to dictionary."""
        result = {
            'id': paper.id,
            'title': paper.title,
            'authors': paper.authors,
            'year': paper.year,
            'doi': paper.doi,
            's2_id': paper.s2_id,
            'citation_count': paper.citation_count,
            'abstract': paper.abstract
        }
        
        if paper.study_metadata:
            result['study_metadata'] = {
                'methodology': paper.study_metadata.methodology,
                'sample_size_baseline': paper.study_metadata.sample_size_baseline,
                'sample_size_endline': paper.study_metadata.sample_size_endline,
                'effect_sizes': paper.study_metadata.effect_sizes
            }
        
        if paper.learning_science_metadata:
            result['learning_science_metadata'] = {
                'learning_domain': paper.learning_science_metadata.learning_domain,
                'intervention_type': paper.learning_science_metadata.intervention_type
            }
        
        return result
```

**Manual Testing Checkpoint:**
```python
# In a Jupyter notebook or Python shell:
from jupyterlab_research_assistant_wwc_copilot.services.db_manager import DatabaseManager

with DatabaseManager() as db:
    # Test adding a paper
    test_paper = {
        'title': 'Test Paper',
        'authors': ['John Doe', 'Jane Smith'],
        'year': 2023,
        'abstract': 'This is a test abstract'
    }
    result = db.add_paper(test_paper)
    print(f"Added paper with ID: {result['id']}")
    
    # Test retrieving papers
    papers = db.get_all_papers()
    print(f"Total papers: {len(papers)}")
```

### Phase 1.2: Semantic Scholar API Client

**File**: `jupyterlab_research_assistant_wwc_copilot/services/semantic_scholar.py`

```python
import requests
from typing import List, Dict, Optional
import time

class SemanticScholarAPI:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    # Rate limit: 100 requests per 5 minutes (free tier)
    # We'll implement simple rate limiting
    def __init__(self, api_key: Optional[str] = None):
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})
        self.last_request_time = 0
        self.min_request_interval = 0.3  # 300ms between requests (conservative)
    
    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict:
        """
        Search for papers using Semantic Scholar API.
        
        Args:
            query: Search query string
            year: Year filter (e.g., "2015-2024" or "2020")
            limit: Maximum number of results (default 20, max 100)
            offset: Pagination offset
        
        Returns:
            Dictionary with 'data' (list of papers) and 'total' (total count)
        """
        self._rate_limit()
        
        params = {
            "query": query,
            "limit": min(limit, 100),  # API max is 100
            "offset": offset,
            "fields": "title,authors,year,abstract,doi,openAccessPdf,paperId,citationCount"
        }
        
        if year:
            params["year"] = year
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/search",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Transform to our format
            papers = []
            for paper in data.get("data", []):
                papers.append({
                    "paperId": paper.get("paperId"),
                    "title": paper.get("title", ""),
                    "authors": [a.get("name", "") for a in paper.get("authors", [])],
                    "year": paper.get("year"),
                    "abstract": paper.get("abstract", ""),
                    "doi": paper.get("doi"),
                    "citation_count": paper.get("citationCount", 0),
                    "open_access_pdf": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
                })
            
            return {
                "data": papers,
                "total": data.get("total", len(papers))
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Semantic Scholar API error: {str(e)}")
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict]:
        """Fetch detailed information for a single paper by Semantic Scholar ID."""
        self._rate_limit()
        
        params = {
            "fields": "title,authors,year,abstract,doi,openAccessPdf,paperId,citationCount,referenceCount"
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/paper/{paper_id}",
                params=params,
                timeout=10
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            paper = response.json()
            
            return {
                "paperId": paper.get("paperId"),
                "title": paper.get("title", ""),
                "authors": [a.get("name", "") for a in paper.get("authors", [])],
                "year": paper.get("year"),
                "abstract": paper.get("abstract", ""),
                "doi": paper.get("doi"),
                "citation_count": paper.get("citationCount", 0),
                "reference_count": paper.get("referenceCount", 0),
                "open_access_pdf": paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Semantic Scholar API error: {str(e)}")
```

**Manual Testing Checkpoint:**
```python
# In a Jupyter notebook:
from jupyterlab_research_assistant_wwc_copilot.services.semantic_scholar import SemanticScholarAPI

api = SemanticScholarAPI()
results = api.search_papers("spaced repetition learning", year="2020-2024", limit=5)
print(f"Found {results['total']} papers")
for paper in results['data'][:3]:
    print(f"- {paper['title']} ({paper['year']})")
```

### Phase 1.3: PDF Parser

**File**: `jupyterlab_research_assistant_wwc_copilot/services/pdf_parser.py`

```python
import fitz  # PyMuPDF
from typing import Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    MAX_PAGES = 200  # Safety limit for very large PDFs
    MAX_TEXT_LENGTH = 500000  # ~500KB of text
    
    def extract_text_and_metadata(self, pdf_path: str) -> Dict:
        """
        Extract full text and metadata from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary with 'title', 'author', 'subject', 'full_text', 'page_count'
        
        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If PDF is corrupted or unreadable
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        try:
            doc = fitz.open(str(pdf_path_obj))
            
            # Extract metadata from PDF properties
            metadata = doc.metadata
            
            # Extract full text (with page limit for safety)
            full_text = ""
            total_pages = len(doc)
            page_count = min(total_pages, self.MAX_PAGES)
            
            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                full_text += page_text + "\n"
                
                # Safety check for extremely long documents
                if len(full_text) > self.MAX_TEXT_LENGTH:
                    logger.warning(f"PDF text truncated at {self.MAX_TEXT_LENGTH} characters")
                    break
            
            doc.close()
            
            return {
                "title": metadata.get("title", "").strip() or None,
                "author": metadata.get("author", "").strip() or None,
                "subject": metadata.get("subject", "").strip() or None,
                "full_text": full_text,
                "page_count": page_count,
                "total_pages": total_pages
            }
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def extract_text_chunk(self, pdf_path: str, max_chars: int = 16000) -> str:
        """
        Extract a chunk of text from the beginning of a PDF (for AI processing).
        
        Args:
            pdf_path: Path to PDF file
            max_chars: Maximum characters to extract
        
        Returns:
            Text chunk (first max_chars characters)
        """
        result = self.extract_text_and_metadata(pdf_path)
        text = result["full_text"]
        return text[:max_chars] if len(text) > max_chars else text
```

**Dependencies to add to `pyproject.toml`:**
```toml
dependencies = [
    # ... existing dependencies ...
    "PyMuPDF>=1.23.0",
    "sqlalchemy>=2.0.0",
    "requests>=2.31.0",
]
```

**Manual Testing Checkpoint:**
```python
# Test with a sample PDF
from jupyterlab_research_assistant_wwc_copilot.services.pdf_parser import PDFParser

parser = PDFParser()
result = parser.extract_text_and_metadata("/path/to/sample.pdf")
print(f"Title: {result['title']}")
print(f"Pages: {result['page_count']}")
print(f"Text length: {len(result['full_text'])} characters")
```

### Phase 1.4: API Routes

**File**: `jupyterlab_research_assistant_wwc_copilot/routes.py`

```python
import json
import os
from pathlib import Path
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from typing import Dict, Any

from .services.semantic_scholar import SemanticScholarAPI
from .services.pdf_parser import PDFParser
from .services.db_manager import DatabaseManager

class LibraryHandler(APIHandler):
    """Handler for library CRUD operations."""
    
    @tornado.web.authenticated
    def get(self):
        """Get all papers in the library."""
        try:
            with DatabaseManager() as db:
                papers = db.get_all_papers()
                self.finish(json.dumps({"status": "success", "data": papers}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))
    
    @tornado.web.authenticated
    def post(self):
        """Add a new paper to the library."""
        try:
            data = self.get_json_body()
            if not data:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "No data provided"}))
                return
            
            with DatabaseManager() as db:
                paper = db.add_paper(data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

class SearchHandler(APIHandler):
    """Handler for searching the library."""
    
    @tornado.web.authenticated
    def get(self):
        """Search papers in the library."""
        try:
            query = self.get_argument("q", "")
            if not query:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "Query parameter 'q' required"}))
                return
            
            with DatabaseManager() as db:
                papers = db.search_papers(query)
                self.finish(json.dumps({"status": "success", "data": papers}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

class DiscoveryHandler(APIHandler):
    """Handler for Semantic Scholar discovery."""
    
    @tornado.web.authenticated
    def get(self):
        """Search Semantic Scholar for papers."""
        try:
            query = self.get_argument("q", "")
            year = self.get_argument("year", None)
            limit = int(self.get_argument("limit", "20"))
            offset = int(self.get_argument("offset", "0"))
            
            if not query:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "Query parameter 'q' required"}))
                return
            
            api = SemanticScholarAPI()
            results = api.search_papers(query, year=year, limit=limit, offset=offset)
            self.finish(json.dumps({"status": "success", "data": results}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

class ImportHandler(APIHandler):
    """Handler for importing PDFs."""
    
    @tornado.web.authenticated
    def post(self):
        """Import a PDF file and extract metadata."""
        try:
            # Get uploaded file
            if 'file' not in self.request.files:
                self.set_status(400)
                self.finish(json.dumps({"status": "error", "message": "No file provided"}))
                return
            
            file_info = self.request.files['file'][0]
            file_content = file_info['body']
            filename = file_info['filename']
            
            # Save file to temporary location
            upload_dir = Path.home() / ".jupyter" / "research_assistant" / "uploads"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / filename
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
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
            
            with DatabaseManager() as db:
                paper = db.add_paper(paper_data)
                self.set_status(201)
                self.finish(json.dumps({"status": "success", "data": paper}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

def setup_route_handlers(web_app):
    """Register all API route handlers."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    route_prefix = "jupyterlab-research-assistant-wwc-copilot"
    
    handlers = [
        (url_path_join(base_url, route_prefix, "library"), LibraryHandler),
        (url_path_join(base_url, route_prefix, "search"), SearchHandler),
        (url_path_join(base_url, route_prefix, "discovery"), DiscoveryHandler),
        (url_path_join(base_url, route_prefix, "import"), ImportHandler),
    ]
    
    web_app.add_handlers(host_pattern, handlers)
```

**Update**: `jupyterlab_research_assistant_wwc_copilot/__init__.py`

```python
from .routes import setup_route_handlers

def _jupyter_server_extension_points():
    return [{
        "module": "jupyterlab_research_assistant_wwc_copilot"
    }]

def _load_jupyter_server_extension(server_app):
    """Load the server extension."""
    setup_route_handlers(server_app.web_app)
    server_app.log.info("jupyterlab_research_assistant_wwc_copilot server extension loaded")
```

**Manual Testing Checkpoint:**
```bash
# After restarting JupyterLab, test endpoints with curl:

# Test library GET
curl http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/library \
  -H "Authorization: token YOUR_TOKEN"

# Test discovery search
curl "http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/discovery?q=spaced+repetition&limit=5" \
  -H "Authorization: token YOUR_TOKEN"

# Test library search
curl "http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/search?q=test" \
  -H "Authorization: token YOUR_TOKEN"
```

---

## Stage 1: Research Library - Frontend

### Phase 1.5: API Client

**File**: `src/api.ts`

```typescript
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
  const response = await requestAPI<APIResponse<Paper[]>>(`search?q=${encodeURIComponent(query)}`, {
    method: 'GET'
  });
  
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
  if (year) params.append('year', year);
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
```

**Update**: `src/request.ts` to handle FormData

```typescript
// ... existing code ...

// In the requestAPI function, update the body handling:
if (init.body instanceof FormData) {
  // Don't set Content-Type for FormData, browser will set it with boundary
  delete headers['Content-Type'];
} else if (init.body) {
  headers['Content-Type'] = 'application/json';
}
```

### Phase 1.6: Research Library Panel Widget

**File**: `src/widgets/ResearchLibraryPanel.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { DiscoveryTab } from './DiscoveryTab';
import { LibraryTab } from './LibraryTab';

interface ResearchLibraryPanelProps {
  // Add any props needed
}

const ResearchLibraryPanelComponent: React.FC<ResearchLibraryPanelProps> = () => {
  const [activeTab, setActiveTab] = useState<'discovery' | 'library'>('discovery');
  
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-panel">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-tabs">
        <button
          className={activeTab === 'discovery' ? 'active' : ''}
          onClick={() => setActiveTab('discovery')}
        >
          Discovery
        </button>
        <button
          className={activeTab === 'library' ? 'active' : ''}
          onClick={() => setActiveTab('library')}
        >
          Library
        </button>
      </div>
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-content">
        {activeTab === 'discovery' && <DiscoveryTab />}
        {activeTab === 'library' && <LibraryTab />}
      </div>
    </div>
  );
};

export class ResearchLibraryPanel extends ReactWidget {
  constructor() {
    super();
    this.addClass('jp-jupyterlab-research-assistant-wwc-copilot-panel-widget');
    this.id = 'research-library-panel';
    this.title.label = 'Research Library';
    this.title.caption = 'Academic Research Library';
    this.title.closable = true;
  }
  
  render(): JSX.Element {
    return <ResearchLibraryPanelComponent />;
  }
}
```

**File**: `src/widgets/DiscoveryTab.tsx`

```typescript
import React, { useState } from 'react';
import { Paper, searchSemanticScholar, importPaper } from '../api';
import { PaperCard } from './PaperCard';

export const DiscoveryTab: React.FC = () => {
  const [query, setQuery] = useState('');
  const [year, setYear] = useState('');
  const [results, setResults] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await searchSemanticScholar(query, year || undefined, 20);
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleImport = async (paper: Paper) => {
    try {
      await importPaper(paper);
      // Show success notification
      alert(`Imported: ${paper.title}`);
    } catch (err) {
      alert(`Import failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };
  
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-discovery">
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-search-bar">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search Semantic Scholar..."
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <input
          type="text"
          value={year}
          onChange={(e) => setYear(e.target.value)}
          placeholder="Year (e.g., 2020-2024)"
          className="jp-jupyterlab-research-assistant-wwc-copilot-input"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading || !query.trim()}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      {error && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
          Error: {error}
        </div>
      )}
      
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-results">
        {results.map((paper) => (
          <PaperCard
            key={paper.paperId || paper.id}
            paper={paper}
            onImport={() => handleImport(paper)}
          />
        ))}
      </div>
    </div>
  );
};
```

**File**: `src/widgets/LibraryTab.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { Paper, getLibrary, searchLibrary } from '../api';
import { PaperCard } from './PaperCard';

export const LibraryTab: React.FC = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
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
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
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
      
      {error && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-error">
          Error: {error}
        </div>
      )}
      
      {isLoading && <div>Loading...</div>}
      
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-papers">
        {papers.length === 0 && !isLoading && (
          <div>No papers found. Use the Discovery tab to search and import papers.</div>
        )}
        {papers.map((paper) => (
          <PaperCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  );
};
```

**File**: `src/widgets/PaperCard.tsx`

```typescript
import React from 'react';
import { Paper } from '../api';

interface PaperCardProps {
  paper: Paper;
  onImport?: () => void;
}

export const PaperCard: React.FC<PaperCardProps> = ({ paper, onImport }) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-card">
      <h3>{paper.title}</h3>
      <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-meta">
        {paper.authors && paper.authors.length > 0 && (
          <div>Authors: {paper.authors.join(', ')}</div>
        )}
        {paper.year && <div>Year: {paper.year}</div>}
        {paper.citation_count !== undefined && (
          <div>Citations: {paper.citation_count}</div>
        )}
      </div>
      {paper.abstract && (
        <div className="jp-jupyterlab-research-assistant-wwc-copilot-paper-abstract">
          {paper.abstract.substring(0, 200)}...
        </div>
      )}
      {onImport && (
        <button
          onClick={onImport}
          className="jp-jupyterlab-research-assistant-wwc-copilot-button"
        >
          Import to Library
        </button>
      )}
    </div>
  );
};
```

### Phase 1.7: Register Panel in Plugin

**Update**: `src/index.ts`

```typescript
import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette } from '@jupyterlab/apputils';
import { ILayoutRestorer } from '@jupyterlab/application';
import { WidgetTracker } from '@jupyterlab/apputils';

import { requestAPI } from './request';
import { ResearchLibraryPanel } from './widgets/ResearchLibraryPanel';

const PLUGIN_ID = 'jupyterlab-research-assistant-wwc-copilot:plugin';

const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  description: 'A JupyterLab extension for academic research management and WWC quality assessment',
  autoStart: true,
  optional: [ISettingRegistry, ICommandPalette, ILayoutRestorer],
  activate: (
    app: JupyterFrontEnd,
    settingRegistry: ISettingRegistry | null,
    palette: ICommandPalette | null,
    restorer: ILayoutRestorer | null
  ) => {
    console.log('JupyterLab extension jupyterlab-research-assistant-wwc-copilot is activated!');
    
    // Create and track the research library panel
    const tracker = new WidgetTracker({
      namespace: 'research-library'
    });
    
    const createPanel = () => {
      const panel = new ResearchLibraryPanel();
      tracker.add(panel);
      app.shell.add(panel, 'left', { rank: 300 });
      return panel;
    };
    
    // Restore panel if it was open before
    if (restorer) {
      restorer.restore(tracker, {
        command: 'jupyterlab-research-assistant-wwc-copilot:open-library',
        name: () => 'research-library'
      });
    }
    
    // Register command to open panel
    app.commands.addCommand('jupyterlab-research-assistant-wwc-copilot:open-library', {
      label: 'Open Research Library',
      execute: () => {
        const existing = tracker.currentWidget;
        if (existing) {
          app.shell.activateById(existing.id);
        } else {
          createPanel();
        }
      }
    });
    
    // Add to command palette
    if (palette) {
      palette.addItem({
        command: 'jupyterlab-research-assistant-wwc-copilot:open-library',
        category: 'Research Assistant'
      });
    }
    
    // Test backend connection
    requestAPI<any>('hello')
      .then(data => {
        console.log('Backend connection successful:', data);
      })
      .catch(reason => {
        console.error(
          `The jupyterlab_research_assistant_wwc_copilot server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
```

**Manual Testing Checkpoint:**
1. Build: `jlpm build`
2. Restart JupyterLab
3. Open command palette (Cmd+Shift+C), search for "Research Library"
4. Click to open panel
5. Test Discovery tab: Search for "spaced repetition"
6. Test Library tab: Should show empty initially
7. Import a paper from Discovery
8. Check Library tab: Should show imported paper
9. Test search in Library tab

---

## Testing Checkpoints

### After Each Backend Feature

1. **Unit Test**: Write a simple test in a Jupyter notebook
2. **API Test**: Use curl or browser dev tools to test endpoint
3. **Error Handling**: Test with invalid inputs
4. **Database**: Verify data is stored correctly

### After Each Frontend Feature

1. **Visual Check**: Does it render correctly?
2. **Interaction**: Do buttons/inputs work?
3. **Console**: Check browser console for errors
4. **Network**: Check Network tab for API calls
5. **State**: Does state update correctly?

### Integration Testing

1. **Full Workflow**: Search → Import → View in Library
2. **Error Scenarios**: Test with network errors, invalid data
3. **Edge Cases**: Empty results, very long text, special characters

---

## Common Issues & Solutions

### Issue: Extension Not Appearing

**Solution:**
```bash
# 1. Check if installed
jupyter labextension list

# 2. Reinstall if needed
pip install -e .
jupyter labextension develop . --overwrite
jupyter server extension enable jupyterlab_research_assistant_wwc_copilot

# 3. Restart JupyterLab (not just refresh browser)
```

### Issue: Backend Routes Not Working

**Solution:**
1. Check server logs for errors
2. Verify route registration in `__init__.py`
3. Test with curl to isolate frontend/backend issues
4. Check authentication token is included

### Issue: Database Errors

**Solution:**
1. Check database file exists: `~/.jupyter/research_assistant/research_library.db`
2. Verify SQLAlchemy models match database schema
3. Check for migration issues
4. Delete database file to reset (if needed)

### Issue: TypeScript Build Errors

**Solution:**
```bash
# Check for type errors
npx tsc --noEmit

# Clean and rebuild
jlpm clean:all
jlpm install
jlpm build
```

### Issue: API Rate Limits

**Solution:**
- Semantic Scholar: Implement caching, batch requests
- AI APIs: Add retry logic with exponential backoff
- Show user-friendly error messages

---

## Next Steps

After completing Stage 1 Core Features:

### Remaining Stage 1 Enhancements

All remaining tasks have been fully documented with complete implementation guides. See:

**📘 Complete Implementation Guide**: `docs/remaining-work-implementation-guide.md`

This guide includes step-by-step instructions for:
1. **PDF Upload UI** - File input component with progress (2-3 hours)
2. **Enhanced Error Handling** - Proper notifications and retry logic (2-3 hours)
3. **AI Metadata Extraction** - Complete integration with settings (4-6 hours)
4. **Paper Detail View** - Full component specification (3-4 hours)
5. **Export Functionality** - CSV, JSON, BibTeX export (2-3 hours)
6. **Enhanced Loading States** - Skeleton loaders (1-2 hours)
7. **Integration Testing** - Complete test plan and examples (3-4 hours)

**Recommended Implementation Order**:
1. PDF Upload UI (easiest, high value)
2. Enhanced Error Handling (improves UX)
3. Enhanced Loading States (quick win)
4. Paper Detail View (user-requested)
5. Export Functionality (useful utility)
6. AI Metadata Extraction (complex but valuable)
7. Integration Testing (quality assurance)

**Total Estimated Time**: 20-30 hours

### Stage 2: WWC Co-Pilot & Synthesis Engine

After completing Stage 1 enhancements, proceed to Stage 2 implementation (see `docs/master-plan.md` for details).

