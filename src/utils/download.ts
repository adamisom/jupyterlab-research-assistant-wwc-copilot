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

