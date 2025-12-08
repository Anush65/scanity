/**
 * API client service for the Scanity frontend
 */
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  ScanRequest,
  ScanResponse,
  ScanResult,
  HealthResponse,
  APIError,
  APISuccess
} from '@/types';

/**
 * Base API client configuration
 */
class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add request timestamp
        config.metadata = { startTime: new Date() };
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        // Log request duration in development
        if (import.meta.env.DEV && response.config.metadata?.startTime) {
          const duration = new Date().getTime() - response.config.metadata.startTime.getTime();
          console.log(`API Request to ${response.config.url} took ${duration}ms`);
        }
        return response;
      },
      (error: AxiosError) => {
        // Handle common error scenarios
        if (error.code === 'ECONNABORTED') {
          error.message = 'Request timeout. Please try again.';
        } else if (error.response?.status === 429) {
          error.message = 'Too many requests. Please wait and try again.';
        } else if (error.response?.status === 503) {
          error.message = 'Service temporarily unavailable. Please try again later.';
        } else if (!error.response && error.request) {
          error.message = 'Network error. Please check your connection.';
        }

        return Promise.reject(error);
      }
    );
  }

  /**
   * Generic GET request
   */
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  /**
   * Generic POST request
   */
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  /**
   * Generic PUT request
   */
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put(url, data);
    return response.data;
  }

  /**
   * Generic DELETE request
   */
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete(url);
    return response.data;
  }

  /**
   * Download file as blob
   */
  async download(url: string, filename?: string): Promise<void> {
    const response = await this.client.get(url, {
      responseType: 'blob',
    });

    // Create download link
    const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = blobUrl;

    // Get filename from Content-Disposition header or use provided name
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition && !filename) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    link.setAttribute('download', filename || 'download');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    return this.get<HealthResponse>('/api/health/');
  }

  /**
   * Simple health check
   */
  async simpleHealthCheck(): Promise<{ status: string; service: string }> {
    return this.get('/api/health/simple');
  }
}

// Create API client instance
export const apiClient = new APIClient();

/**
 * Scan API service
 */
export class ScanAPI {
  /**
   * Initiate a new scan
   */
  static async initiateScan(request: ScanRequest): Promise<ScanResponse> {
    try {
      const response = await apiClient.post<ScanResponse>('/api/scan/', request);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Get scan results by ID
   */
  static async getScanResults(scanId: string): Promise<ScanResult> {
    try {
      const result = await apiClient.get<ScanResult>(`/api/scan/${scanId}`);
      return result;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Download PDF report
   */
  static async downloadPDF(scanId: string, filename?: string): Promise<void> {
    try {
      const defaultFilename = filename || `scanity-report-${scanId}.pdf`;
      await apiClient.download(`/api/scan/${scanId}/pdf`, defaultFilename);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Delete scan results
   */
  static async deleteScan(scanId: string): Promise<{ message: string }> {
    try {
      const result = await apiClient.delete<{ message: string }>(`/api/scan/${scanId}`);
      return result;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * List all scans (for testing/monitoring)
   */
  static async listScans(): Promise<{ scans: Partial<ScanResult>[]; total: number }> {
    try {
      const result = await apiClient.get<{ scans: Partial<ScanResult>[]; total: number }>('/api/scan/');
      return result;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  /**
   * Poll for scan results
   */
  static async pollScanResults(
    scanId: string,
    onUpdate?: (result: ScanResult) => void,
    intervalMs: number = 2000,
    maxAttempts: number = 30
  ): Promise<ScanResult> {
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const result = await this.getScanResults(scanId);

        if (onUpdate) {
          onUpdate(result);
        }

        if (result.status === 'completed') {
          return result;
        }

        if (result.status === 'failed') {
          throw new Error(result.error_message || 'Scan failed');
        }

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        attempts++;
      } catch (error) {
        if (attempts === maxAttempts - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        attempts++;
      }
    }

    throw new Error('Scan timeout: Maximum polling attempts reached');
  }

  /**
   * Handle API errors consistently
   */
  private static handleError(error: any): Error {
    if (error?.response?.data) {
      const apiError = error.response.data as APIError;
      return new Error(apiError.error || 'An unknown error occurred');
    } else if (error?.message) {
      return new Error(error.message);
    } else {
      return new Error('An unexpected error occurred');
    }
  }
}

/**
 * Utility functions for common operations
 */
export const APIUtils = {
  /**
   * Check if API is available
   */
  async isAPIAvailable(): Promise<boolean> {
    try {
      await apiClient.simpleHealthCheck();
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Get API status
   */
  async getAPIStatus(): Promise<HealthResponse | null> {
    try {
      return await apiClient.healthCheck();
    } catch {
      return null;
    }
  },

  /**
   * Extract error message from API response
   */
  extractErrorMessage(error: any): string {
    if (error?.response?.data?.error) {
      return error.response.data.error;
    } else if (error?.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred';
    }
  },

  /**
   * Check if error is a network error
   */
  isNetworkError(error: any): boolean {
    return !error.response && !!error.request;
  },

  /**
   * Check if error is a timeout error
   */
  isTimeoutError(error: any): boolean {
    return error.code === 'ECONNABORTED' || error.message?.includes('timeout');
  },

  /**
   * Check if error is a server error
   */
  isServerError(error: any): boolean {
    return error.response?.status >= 500;
  },

  /**
   * Check if error is a client error
   */
  isClientError(error: any): boolean {
    const status = error.response?.status;
    return status >= 400 && status < 500;
  },

  /**
   * Check if error is an authentication error
   */
  isAuthError(error: any): boolean {
    return error.response?.status === 401;
  },

  /**
   * Check if error is a permission error
   */
  isPermissionError(error: any): boolean {
    return error.response?.status === 403;
  },

  /**
   * Check if error is a not found error
   */
  isNotFoundError(error: any): boolean {
    return error.response?.status === 404;
  },

  /**
   * Check if error is a rate limit error
   */
  isRateLimitError(error: any): boolean {
    return error.response?.status === 429;
  },

  /**
   * Check if error is a validation error
   */
  isValidationError(error: any): boolean {
    return error.response?.status === 422;
  }
};

// Export default API client
export default apiClient;