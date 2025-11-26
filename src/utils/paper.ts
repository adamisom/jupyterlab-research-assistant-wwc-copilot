import { IPaper } from '../api';

/**
 * Get a unique key for a paper, used for React keys.
 * @param paper - Paper object
 * @returns Unique key string
 */
export function getPaperKey(paper: IPaper): string {
  return paper.paperId || paper.id?.toString() || `paper-${Math.random()}`;
}

/**
 * Check if a paper has a full PDF (not just metadata).
 * @param paper - Paper object
 * @returns True if paper has pdf_path or full_text
 */
export function hasFullPDF(paper: IPaper): boolean {
  return !!(paper.pdf_path || paper.full_text);
}
