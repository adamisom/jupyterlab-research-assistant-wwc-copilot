# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-XX

### Added

- **PDF Viewing**: Support for viewing uploaded PDFs via blob URLs in new browser tabs
- **Open Access PDF Links**: Display and link to open access PDFs from external sources (Semantic Scholar, OpenAlex)
- **Abstract Extraction**: Extract abstracts from uploaded PDFs (first page, first paragraph(s))
- **Authors & Year Extraction**: Extract authors and publication year from PDF first page
- **Library UI Improvements**:
  - Show Authors and Year in Library list instead of abstract snippet
  - Display "could not detect" when extraction fails
  - Clickable "Full Local PDF" badge in Library list
  - Enhanced PDF link styling with hover effects

### Fixed

- **Abstract Extraction**: Stop extraction at "Keywords:" marker
- **Library Ordering**: Library now shows most recent additions first
- **PDF Display**: Fixed PDF viewing to use blob URLs instead of direct backend serving
- **Test Configuration**: Fixed pytest wrapper script and test discovery paths

### Changed

- **Abstract Extraction**: Improved logic to remove authors from abstract text (needs further refinement)
- **Library Display**: Replaced abstract snippet with Authors/Year fields for better metadata visibility

## [0.1.0] - 2025-11-25

### Added

- **[User Guide](./USER_GUIDE.md)**: Comprehensive user documentation covering all features, workflows, and best practices
- Stage 2 enhancements (all features now complete):
  - **Enhanced WWC UI**: Multi-step wizard interface with progress
    indicators and localStorage persistence
  - **Subgroup Analysis**: Meta-analysis by subgroups (age group,
    intervention type, learning domain)
  - **Publication Bias Assessment**: Egger's test and funnel plots for
    detecting publication bias
  - **Advanced Conflict Detection**: AI-extracted findings preview for
    better conflict identification
  - **Sensitivity Analysis**: Leave-one-out analysis and influence
    diagnostics to identify influential studies
- Stage 2 enhancements guide
  (`docs/stage-2-enhancements-implementation-guide.md`) for
  implementation reference

### Fixed

- **Conflict Detection**: Fixed input format for cross-encoder NLI model
  (now uses tuple format instead of string concatenation)
- **Conflict Detection**: Added topic filtering to reduce false positives
  when findings are about different interventions/outcomes
- **Meta-Analysis**: Suppressed harmless sqrt() warnings from statsmodels
  when tau² is negative (common with 2 studies or low heterogeneity)

### Changed

- Updated documentation to reflect Stage 2 completion (core features +
  enhancements)
- Updated main README with complete feature status
- Conflict detection now filters out comparisons between findings about
  different topics by default (reduces false positives)

### Completed

- **Stage 1: Research Library & Discovery Engine** - Fully implemented with:
  - Semantic Scholar API integration for paper discovery
  - OpenAlex API integration with automatic fallback when Semantic Scholar fails
  - PDF parsing and text extraction
  - AI-powered metadata extraction (configurable: Claude, OpenAI, Ollama)
  - SQLite database for paper storage and search
  - Research Library sidebar panel with Discovery and Library tabs
  - PDF viewing support
  - Export functionality (CSV, JSON, BibTeX)

- **Stage 2: WWC Co-Pilot & Synthesis Engine** - Fully implemented with:
  - Core features: WWC quality assessment, meta-analysis, conflict
    detection
  - Enhanced features: Multi-step WWC wizard, subgroup analysis,
    publication bias assessment, advanced conflict detection, sensitivity
    analysis

<!-- <START NEW CHANGELOG ENTRY> -->

<!-- <END NEW CHANGELOG ENTRY> -->
