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
    throw new ServerConnection.NetworkError(error as any);
  }

  let data: any = await response.text();

  if (data.length > 0) {
    try {
      data = JSON.parse(data);
    } catch (error) {
      console.error('Not a JSON response body.', response, error);
    }
  }

  if (!response.ok) {
    throw new ServerConnection.ResponseError(response, data.message || data);
  }

  return data;
}
