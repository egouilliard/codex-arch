/**
 * Tests for the formatters.ts utility functions
 */

import { formatAsTable, formatAsJSON, formatAsTree, formatAsPlain } from '../../src/utils/formatters';

describe('formatters utility', () => {
  describe('formatAsTable', () => {
    it('should format data as a table', () => {
      const testData = [
        { name: 'file1.ts', count: 5 },
        { name: 'file2.ts', count: 3 }
      ];
      const headers = ['name', 'count'];
      
      const result = formatAsTable(testData, headers);
      
      // Check that result contains our data values
      expect(result).toContain('file1.ts');
      expect(result).toContain('file2.ts');
      expect(result).toContain('5');
      expect(result).toContain('3');
    });

    it('should handle empty data', () => {
      const result = formatAsTable([], ['name', 'count']);
      expect(result).toBeDefined();
    });
  });

  describe('formatAsJSON', () => {
    it('should format data as JSON with pretty printing', () => {
      const testData = { key: 'value' };
      const result = formatAsJSON(testData, true);
      expect(result).toBe('{\n  "key": "value"\n}');
    });

    it('should format data as compact JSON', () => {
      const testData = { key: 'value' };
      const result = formatAsJSON(testData, false);
      expect(result).toBe('{"key":"value"}');
    });
  });

  describe('formatAsPlain', () => {
    it('should format array data as plain text', () => {
      const testData = ['line1', 'line2'];
      const result = formatAsPlain(testData);
      expect(result).toBe('line1\nline2');
    });
  });
}); 