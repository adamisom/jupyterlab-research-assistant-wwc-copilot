import { IAPIResponse } from '../api';

/**
 * Handle API response and extract data or throw error.
 * @param response - API response object
 * @param errorMessage - Default error message if response is error
 * @returns Extracted data from response
 * @throws Error if response status is error or data is missing
 */
export function handleAPIResponse<T>(
  response: IAPIResponse<T>,
  errorMessage: string
): T {
  if (response.status === 'error') {
    throw new Error(response.message || errorMessage);
  }
  if (!response.data) {
    throw new Error(errorMessage);
  }
  return response.data;
}
