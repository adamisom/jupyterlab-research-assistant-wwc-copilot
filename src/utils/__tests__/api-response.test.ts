import { handleAPIResponse } from '../api-response';
import { IAPIResponse } from '../../api';

describe('handleAPIResponse', () => {
  it('should return data when response is successful', () => {
    const response: IAPIResponse<string> = {
      status: 'success',
      data: 'test data'
    };
    expect(handleAPIResponse(response, 'Error')).toBe('test data');
  });

  it('should throw error when response status is error', () => {
    const response: IAPIResponse<string> = {
      status: 'error',
      message: 'Custom error message'
    };
    expect(() => handleAPIResponse(response, 'Default error')).toThrow(
      'Custom error message'
    );
  });

  it('should throw default error message when response status is error without message', () => {
    const response: IAPIResponse<string> = {
      status: 'error'
    };
    expect(() => handleAPIResponse(response, 'Default error')).toThrow(
      'Default error'
    );
  });

  it('should throw error when data is missing', () => {
    const response: IAPIResponse<string> = {
      status: 'success'
      // data is undefined
    };
    expect(() => handleAPIResponse(response, 'Data missing')).toThrow(
      'Data missing'
    );
  });

  it('should handle complex data types', () => {
    const complexData = {
      id: 1,
      items: ['a', 'b', 'c']
    };
    const response: IAPIResponse<typeof complexData> = {
      status: 'success',
      data: complexData
    };
    expect(handleAPIResponse(response, 'Error')).toEqual(complexData);
  });
});
