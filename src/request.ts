import { URLExt } from '@jupyterlab/coreutils';

import { ServerConnection } from '@jupyterlab/services';

/**
 * Call the server extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
export async function requestAPI<T>(
  endPoint = '',
  init: RequestInit = {}
): Promise<T> {
  // Make request to Jupyter API
  const settings = ServerConnection.makeSettings();
  const requestUrl = URLExt.join(
    settings.baseUrl,
    'jupyterlab-research-assistant-wwc-copilot', // our server extension's API namespace
    endPoint
  );

  // Handle FormData - don't set Content-Type, browser will set it with boundary
  const headers: HeadersInit = {};
  if (init.body instanceof FormData) {
    // Don't set Content-Type for FormData
  } else if (init.body) {
    headers['Content-Type'] = 'application/json';
  }

  const requestInit: RequestInit = {
    ...init,
    headers: {
      ...headers,
      ...(init.headers || {})
    }
  };

  let response: Response;
  try {
    response = await ServerConnection.makeRequest(
      requestUrl,
      requestInit,
      settings
    );
  } catch (error) {
    // NetworkError constructor accepts unknown error type
    const networkError =
      error instanceof TypeError ? error : new TypeError(String(error));
    throw new ServerConnection.NetworkError(networkError);
  }

  let dataText = await response.text();
  let data: unknown = dataText;

  if (dataText.length > 0) {
    try {
      data = JSON.parse(dataText);
    } catch (error) {
      console.error('Not a JSON response body.', response, error);
    }
  }

  if (!response.ok) {
    const errorMessage =
      (data && typeof data === 'object' && 'message' in data
        ? String((data as { message: unknown }).message)
        : String(data)) || 'Request failed';
    throw new ServerConnection.ResponseError(response, errorMessage);
  }

  return data as T;
}
