import { getPaperKey } from '../paper';
import { IPaper } from '../../api';

describe('getPaperKey', () => {
  it('should return paperId when available', () => {
    const paper: IPaper = {
      paperId: 'test-id-123',
      title: 'Test Paper',
      authors: []
    };
    expect(getPaperKey(paper)).toBe('test-id-123');
  });

  it('should return id as string when paperId is not available', () => {
    const paper: IPaper = {
      id: 42,
      title: 'Test Paper',
      authors: []
    };
    expect(getPaperKey(paper)).toBe('42');
  });

  it('should return generated key when neither paperId nor id is available', () => {
    const paper: IPaper = {
      title: 'Test Paper',
      authors: []
    };
    const key = getPaperKey(paper);
    expect(key).toMatch(/^paper-/);
  });

  it('should prefer paperId over id', () => {
    const paper: IPaper = {
      id: 42,
      paperId: 'preferred-id',
      title: 'Test Paper',
      authors: []
    };
    expect(getPaperKey(paper)).toBe('preferred-id');
  });
});
