import {
  downloadBlob,
  downloadJSON,
  downloadCSV,
  downloadFromURL
} from '../download';

// Mock DOM methods
const mockClick = jest.fn();
const mockAppendChild = jest.fn();
const mockRemoveChild = jest.fn();
const mockCreateElement = jest.fn(() => ({
  click: mockClick,
  href: '',
  download: ''
}));

beforeEach(() => {
  jest.clearAllMocks();
  document.createElement =
    mockCreateElement as unknown as typeof document.createElement;
  document.body.appendChild = mockAppendChild;
  document.body.removeChild = mockRemoveChild;
  window.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
  window.URL.revokeObjectURL = jest.fn();
});

describe('download utilities', () => {
  describe('downloadBlob', () => {
    it('should create anchor element and trigger download', () => {
      const blob = new Blob(['test'], { type: 'text/plain' });
      const filename = 'test.txt';

      downloadBlob(blob, filename);

      expect(mockCreateElement).toHaveBeenCalledWith('a');
      expect(mockAppendChild).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
      expect(mockRemoveChild).toHaveBeenCalled();
      expect(window.URL.createObjectURL).toHaveBeenCalledWith(blob);
      expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock-url');
    });
  });

  describe('downloadJSON', () => {
    it('should create JSON blob and download it', () => {
      const data = { key: 'value', number: 42 };
      const filename = 'data';

      downloadJSON(data, filename);

      expect(mockCreateElement).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
    });

    it('should format JSON with indentation', () => {
      const data = { a: 1, b: 2 };
      downloadJSON(data, 'test');

      // Verify blob was created with proper JSON content
      expect(window.URL.createObjectURL).toHaveBeenCalled();
      const blobCall = (window.URL.createObjectURL as jest.Mock).mock
        .calls[0][0];
      expect(blobCall).toBeInstanceOf(Blob);
      expect(blobCall.type).toBe('application/json');
    });
  });

  describe('downloadCSV', () => {
    it('should create CSV blob and download it', () => {
      const csvContent = 'col1,col2\nval1,val2';
      const filename = 'data';

      downloadCSV(csvContent, filename);

      expect(mockCreateElement).toHaveBeenCalled();
      expect(mockClick).toHaveBeenCalled();
    });

    it('should create blob with CSV content type', () => {
      const csvContent = 'header1,header2';
      downloadCSV(csvContent, 'test');

      expect(window.URL.createObjectURL).toHaveBeenCalled();
      const blobCall = (window.URL.createObjectURL as jest.Mock).mock
        .calls[0][0];
      expect(blobCall).toBeInstanceOf(Blob);
      expect(blobCall.type).toBe('text/csv');
    });
  });

  describe('downloadFromURL', () => {
    it('should fetch and download file from URL', async () => {
      const mockBlob = new Blob(['content'], { type: 'text/plain' });
      window.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(mockBlob)
        } as Response)
      ) as typeof fetch;

      await downloadFromURL('https://example.com/file.txt', 'file.txt');

      expect(window.fetch).toHaveBeenCalledWith('https://example.com/file.txt');
      expect(mockClick).toHaveBeenCalled();
    });

    it('should throw error on failed fetch', async () => {
      window.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          statusText: 'Not Found'
        } as Response)
      ) as typeof fetch;

      await expect(
        downloadFromURL('https://example.com/missing.txt', 'missing.txt')
      ).rejects.toThrow('Failed to download file: Not Found');
    });
  });
});
