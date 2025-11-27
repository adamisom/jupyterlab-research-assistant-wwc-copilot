/**
 * Utility functions for downloading files from the browser.
 */

/**
 * Download a blob as a file.
 * @param blob - The blob to download
 * @param filename - The filename for the downloaded file
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Download data as a JSON file.
 * @param data - The data to download (will be JSON stringified)
 * @param filename - The filename for the downloaded file (without .json extension)
 */
export function downloadJSON(data: unknown, filename: string): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  downloadBlob(blob, `${filename}.json`);
}

/**
 * Download data as a CSV file.
 * @param csvContent - The CSV content as a string
 * @param filename - The filename for the downloaded file (without .csv extension)
 */
export function downloadCSV(csvContent: string, filename: string): void {
  const blob = new Blob([csvContent], { type: 'text/csv' });
  downloadBlob(blob, `${filename}.csv`);
}

/**
 * Download a file from a URL.
 * @param url - The URL to download from
 * @param filename - The filename for the downloaded file
 */
export async function downloadFromURL(
  url: string,
  filename: string
): Promise<void> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download file: ${response.statusText}`);
  }
  const blob = await response.blob();
  downloadBlob(blob, filename);
}

/**
 * Open a PDF file in a new browser tab using a blob URL.
 * This fetches the PDF from the backend and opens it using the browser's native PDF viewer.
 * @param url - The URL to fetch the PDF from
 */
export async function openPDFInNewTab(url: string): Promise<void> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch PDF: ${response.statusText}`);
  }

  // Get the binary data as an ArrayBuffer first
  const arrayBuffer = await response.arrayBuffer();

  // Create a Blob with explicit PDF MIME type
  const blob = new Blob([arrayBuffer], { type: 'application/pdf' });

  // Create blob URL
  const blobUrl = window.URL.createObjectURL(blob);

  // Open in new tab
  const newWindow = window.open(blobUrl, '_blank');
  if (newWindow) {
    // Clean up blob URL after a delay to allow the browser to load it
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
    }, 1000);
  } else {
    // If popup was blocked, clean up immediately
    window.URL.revokeObjectURL(blobUrl);
    throw new Error('Popup blocked. Please allow popups for this site.');
  }
}
