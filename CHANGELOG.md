# Changelog

## [Unreleased]

### Fixed

- **Conflict Detection**: Fixed input format for cross-encoder NLI model (now uses tuple format instead of string concatenation)
- **Conflict Detection**: Added topic filtering to reduce false positives when findings are about different interventions/outcomes
- **Meta-Analysis**: Suppressed harmless sqrt() warnings from statsmodels when tau² is negative (common with 2 studies or low heterogeneity)

### Added

- Stage 2 enhancements (all features now complete):
  - **Enhanced WWC UI**: Multi-step wizard interface with progress indicators and localStorage persistence
  - **Subgroup Analysis**: Meta-analysis by subgroups (age group, intervention type, learning domain)
  - **Publication Bias Assessment**: Egger's test and funnel plots for detecting publication bias
  - **Advanced Conflict Detection**: AI-extracted findings preview for better conflict identification
  - **Sensitivity Analysis**: Leave-one-out analysis and influence diagnostics to identify influential studies
- Stage 2 enhancements guide (`docs/stage-2-enhancements-implementation-guide.md`) for implementation reference

### Changed

- Updated documentation to reflect Stage 2 completion (core features + enhancements)
- Updated main README with complete feature status
- Conflict detection now filters out comparisons between findings about different topics by default (reduces false positives)

### Completed

- **Stage 1: Research Library & Discovery Engine** - Fully implemented with:
  - Semantic Scholar API integration for paper discovery
  - PDF parsing and text extraction
  - AI-powered metadata extraction (configurable: Claude, OpenAI, Ollama)
  - SQLite database for paper storage and search
  - Research Library sidebar panel with Discovery and Library tabs
  - Export functionality (CSV, JSON, BibTeX)

- **Stage 2: WWC Co-Pilot & Synthesis Engine** - Fully implemented with:
  - Core features: WWC quality assessment, meta-analysis, conflict detection
  - Enhanced features: Multi-step WWC wizard, subgroup analysis, publication bias assessment, advanced conflict detection, sensitivity analysis

<!-- <START NEW CHANGELOG ENTRY> -->

<!-- <END NEW CHANGELOG ENTRY> -->
