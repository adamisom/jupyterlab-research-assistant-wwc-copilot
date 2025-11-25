import { showDialog, Dialog } from '@jupyterlab/apputils';

/**
 * Show an error notification to the user.
 * @param title - Error title
 * @param message - Error message
 * @param error - Optional error object for logging
 */
export function showError(title: string, message: string, error?: Error): void {
  console.error(`${title}: ${message}`, error);
  showDialog({
    title,
    body: message,
    buttons: [Dialog.okButton()]
  });
}

/**
 * Show a success notification to the user.
 * @param title - Success title
 * @param message - Success message
 */
export function showSuccess(title: string, message: string): void {
  console.log(`${title}: ${message}`);
  showDialog({
    title,
    body: message,
    buttons: [Dialog.okButton()]
  });
}

/**
 * Show a warning notification to the user.
 * @param title - Warning title
 * @param message - Warning message
 */
export function showWarning(title: string, message: string): void {
  console.warn(`${title}: ${message}`);
  showDialog({
    title,
    body: message,
    buttons: [Dialog.okButton()]
  });
}
