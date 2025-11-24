# API Contract for Research Library

**Purpose**: Shared contract between backend and frontend developers to ensure compatibility.

**Base URL**: `/jupyterlab-research-assistant-wwc-copilot`

**All responses follow this format**:
```typescript
{
  status: "success" | "error",
  data?: T,  // Present if status is "success"
  message?: string  // Present if status is "error" or for additional info
}
```

---

## Endpoints

### 1. GET `/library`

**Description**: Get all papers in the library.

**Request**: No body, no query parameters

**Response**:
```typescript
{
  status: "success",
  data: Paper[]
}
```

**Error Response**:
```typescript
{
  status: "error",
  message: "Error description"
}
```

---

### 2. POST `/library`

**Description**: Add a new paper to the library.

**Request Body**:
```typescript
Paper  // See Paper interface below
```

**Response**:
```typescript
{
  status: "success",
  data: Paper  // Paper with generated ID
}
```

**Status Code**: 201 (Created)

**Error Response**:
```typescript
{
  status: "error",
  message: "Error description"
}
```

---

### 3. GET `/search?q={query}`

**Description**: Search papers in the library.

**Query Parameters**:
- `q` (required): Search query string

**Response**:
```typescript
{
  status: "success",
  data: Paper[]
}
```

**Error Response**:
```typescript
{
  status: "error",
  message: "Query parameter 'q' required"
}
```

---

### 4. GET `/discovery?q={query}&year={year}&limit={limit}&offset={offset}`

**Description**: Search Semantic Scholar for papers.

**Query Parameters**:
- `q` (required): Search query string
- `year` (optional): Year filter (e.g., "2020-2024" or "2020")
- `limit` (optional): Maximum results (default: 20, max: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```typescript
{
  status: "success",
  data: {
    data: Paper[],  // List of papers from Semantic Scholar
    total: number    // Total number of results available
  }
}
```

**Error Response**:
```typescript
{
  status: "error",
  message: "Query parameter 'q' required" | "Semantic Scholar API error: ..."
}
```

---

### 5. POST `/import`

**Description**: Import a PDF file and extract metadata.

**Request**: `multipart/form-data`
- `file` (required): PDF file

**Response**:
```typescript
{
  status: "success",
  data: Paper  // Paper with extracted metadata
}
```

**Status Code**: 201 (Created)

**Error Response**:
```typescript
{
  status: "error",
  message: "No file provided" | "Failed to parse PDF: ..."
}
```

---

## Data Types

### Paper Interface

```typescript
interface Paper {
  // Core fields
  id?: number;                    // Database ID (present after saving)
  paperId?: string;               // Semantic Scholar paper ID
  title: string;                   // Required
  authors: string[];              // Array of author names
  year?: number;                  // Publication year
  doi?: string;                   // Digital Object Identifier
  s2_id?: string;                 // Semantic Scholar ID (same as paperId)
  citation_count?: number;        // Number of citations
  abstract?: string;              // Paper abstract
  full_text?: string;             // Extracted PDF text (may be large)
  
  // Metadata (optional, present if extracted)
  study_metadata?: {
    methodology?: string;         // e.g., "RCT", "Quasi-experimental"
    sample_size_baseline?: number;
    sample_size_endline?: number;
    effect_sizes?: Record<string, {  // Outcome name -> effect size
      d: number;                    // Cohen's d
      se: number;                   // Standard error
    }>;
  };
  
  learning_science_metadata?: {
    learning_domain?: string;       // e.g., "cognitive", "affective"
    intervention_type?: string;    // e.g., "Spaced Repetition"
  };
}
```

### Example Paper (from Semantic Scholar)

```json
{
  "paperId": "1234567890",
  "title": "The Effect of Spaced Repetition on Long-Term Retention",
  "authors": ["John Doe", "Jane Smith"],
  "year": 2023,
  "abstract": "This study examines...",
  "doi": "10.1234/example",
  "citation_count": 42,
  "open_access_pdf": "https://example.com/paper.pdf"
}
```

### Example Paper (from Database)

```json
{
  "id": 1,
  "title": "The Effect of Spaced Repetition on Long-Term Retention",
  "authors": ["John Doe", "Jane Smith"],
  "year": 2023,
  "abstract": "This study examines...",
  "doi": "10.1234/example",
  "s2_id": "1234567890",
  "citation_count": 42,
  "study_metadata": {
    "methodology": "RCT",
    "sample_size_baseline": 100,
    "sample_size_endline": 95,
    "effect_sizes": {
      "retention_test": {
        "d": 0.75,
        "se": 0.15
      }
    }
  },
  "learning_science_metadata": {
    "learning_domain": "cognitive",
    "intervention_type": "Spaced Repetition"
  }
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (resource created)
- `400 Bad Request`: Invalid request (missing parameters, invalid data)
- `401 Unauthorized`: Authentication required (handled by Jupyter Server)
- `500 Internal Server Error`: Server error

### Error Response Format

All errors return:
```typescript
{
  status: "error",
  message: string  // Human-readable error description
}
```

### Common Error Messages

- `"Query parameter 'q' required"` - Missing required query parameter
- `"No data provided"` - Missing request body
- `"No file provided"` - Missing file in multipart request
- `"Semantic Scholar API error: ..."` - External API error
- `"Failed to parse PDF: ..."` - PDF parsing error
- `"Database error: ..."` - Database operation failed

---

## Authentication

All endpoints require Jupyter Server authentication. The frontend should use `requestAPI()` helper which automatically includes authentication tokens.

**Frontend Implementation**:
```typescript
import { requestAPI } from './request';

// requestAPI automatically handles authentication
const response = await requestAPI<APIResponse<Paper[]>>('library', {
  method: 'GET'
});
```

**Backend Implementation**:
```python
from jupyter_server.base.handlers import APIHandler
import tornado

class LibraryHandler(APIHandler):
    @tornado.web.authenticated  # Required decorator
    def get(self):
        # Handler code
        pass
```

---

## Testing

### Backend Testing (with curl)

```bash
# Get Jupyter token
TOKEN=$(jupyter lab list | grep token | awk '{print $NF}')

# Test GET /library
curl -H "Authorization: token $TOKEN" \
  http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/library

# Test GET /discovery
curl -H "Authorization: token $TOKEN" \
  "http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/discovery?q=spaced+repetition&limit=5"

# Test POST /library
curl -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Paper","authors":["Author 1"],"year":2023}' \
  http://localhost:8888/jupyterlab-research-assistant-wwc-copilot/library
```

### Frontend Testing (with mocks)

```typescript
// Temporary mock for development
export async function getLibrary(): Promise<Paper[]> {
  if (process.env.NODE_ENV === 'development' && USE_MOCK) {
    return [
      {
        id: 1,
        title: "Mock Paper",
        authors: ["Mock Author"],
        year: 2023,
        abstract: "This is a mock paper for testing"
      }
    ];
  }
  
  // Real implementation
  const response = await requestAPI<APIResponse<Paper[]>>('library', {
    method: 'GET'
  });
  
  if (response.status === 'error') {
    throw new Error(response.message || 'Failed to fetch library');
  }
  
  return response.data || [];
}
```

---

## Version History

- **v1.0** (Initial): Basic CRUD operations, Semantic Scholar integration, PDF import

---

## Notes for Developers

### Backend Developers

- Always return the standard response format
- Include descriptive error messages
- Validate input data before processing
- Use proper HTTP status codes
- Handle file uploads with appropriate size limits

### Frontend Developers

- Always check `response.status` before accessing `response.data`
- Handle errors gracefully with user-friendly messages
- Use TypeScript interfaces for type safety
- Mock API responses during development if backend is not ready
- Update mocks when API contract changes

### Both Teams

- **Any changes to this contract must be communicated immediately**
- Update this document when adding new endpoints
- Test integration frequently (at least once per day)
- Use the shared TypeScript interfaces in `src/api.ts`

