import { formatPercent, formatNumber, formatCI } from '../format';

describe('format utilities', () => {
  describe('formatPercent', () => {
    it('should format decimal as percentage with default decimals', () => {
      expect(formatPercent(0.85)).toBe('85.0%');
      expect(formatPercent(0.5)).toBe('50.0%');
      expect(formatPercent(1.0)).toBe('100.0%');
    });

    it('should format decimal as percentage with custom decimals', () => {
      expect(formatPercent(0.8567, 2)).toBe('85.67%');
      expect(formatPercent(0.5, 0)).toBe('50%');
      expect(formatPercent(0.1234, 3)).toBe('12.340%');
    });

    it('should handle zero and edge cases', () => {
      expect(formatPercent(0)).toBe('0.0%');
      expect(formatPercent(0.001, 3)).toBe('0.100%');
    });
  });

  describe('formatNumber', () => {
    it('should format number with default decimals', () => {
      expect(formatNumber(3.14159)).toBe('3.14');
      expect(formatNumber(42)).toBe('42.00');
    });

    it('should format number with custom decimals', () => {
      expect(formatNumber(3.14159, 3)).toBe('3.142');
      expect(formatNumber(42, 0)).toBe('42');
      expect(formatNumber(0.123456, 4)).toBe('0.1235');
    });

    it('should handle zero and negative numbers', () => {
      expect(formatNumber(0)).toBe('0.00');
      expect(formatNumber(-1.5, 1)).toBe('-1.5');
    });
  });

  describe('formatCI', () => {
    it('should format confidence interval with default decimals', () => {
      expect(formatCI(0.123, 0.456)).toBe('[0.123, 0.456]');
      expect(formatCI(-0.5, 0.5)).toBe('[-0.500, 0.500]');
    });

    it('should format confidence interval with custom decimals', () => {
      expect(formatCI(0.1234, 0.5678, 2)).toBe('[0.12, 0.57]');
      expect(formatCI(1.234, 5.678, 1)).toBe('[1.2, 5.7]');
    });

    it('should handle edge cases', () => {
      expect(formatCI(0, 0)).toBe('[0.000, 0.000]');
      expect(formatCI(-1, 1, 0)).toBe('[-1, 1]');
    });
  });
});
