import { IPaper } from '../api';

/**
 * Get a unique key for a paper, used for React keys.
 * @param paper - Paper object
 * @returns Unique key string
 */
export function getPaperKey(paper: IPaper): string {
  return paper.paperId || paper.id?.toString() || `paper-${Math.random()}`;
}
