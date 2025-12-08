/**
 * Custom hook for managing scan operations
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { ScanAPI } from '@/services/api';
import {
  UseScanReturn,
  ScanStatus,
  ScanResult,
  ScanOptions,
  ScanRequest
} from '@/types';
import { validateUrl } from '@/utils/validation';

/**
 * Hook for managing website scanning operations
 */
export const useScan = (): UseScanReturn => {
  const [scanState, setScanState] = useState<ScanStatus>('idle');
  const [currentScan, setCurrentScan] = useState<ScanResult | null>(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * Default scan options
   */
  const defaultOptions: ScanOptions = {
    include_screenshot: true,
    scan_depth: 'standard',
    mobile_view: false
  };

  /**
   * Progress messages for different scan phases
   */
  const progressMessages = [
    'Initializing browser...',
    'Loading website...',
    'Analyzing security...',
    'Checking performance...',
    'Evaluating code quality...',
    'Generating recommendations...'
  ];

  /**
   * Start a new scan
   */
  const startScan = useCallback(async (
    url: string,
    options: Partial<ScanOptions> = {}
  ): Promise<void> => {
    try {
      // Reset state
      setError(null);
      setProgress(0);
      setScanState('scanning');
      setCurrentScan(null);

      // Validate URL
      const validationError = validateUrl(url);
      if (validationError) {
        setError(validationError.message);
        setScanState('idle');
        toast.error(validationError.message);
        return;
      }

      // Merge options with defaults
      const scanOptions: ScanOptions = { ...defaultOptions, ...options };

      // Create scan request
      const scanRequest: ScanRequest = {
        url: url.trim(),
        options: scanOptions
      };

      // Cancel any existing scan
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      // Create new abort controller
      abortControllerRef.current = new AbortController();

      // Show initial toast
      const toastId = toast.loading('Starting scan...');

      try {
        // Initiate scan
        const response = await ScanAPI.initiateScan(scanRequest);

        // Create initial scan result
        const initialScan: ScanResult = {
          scan_id: response.scan_id,
          url: url.trim(),
          status: 'pending',
          health_score: 0,
          categories: {
            security: { score: 0, issues_count: 0, issues: [] },
            performance: { score: 0, issues_count: 0, issues: [] },
            quality: { score: 0, issues_count: 0, issues: [] }
          },
          metrics: null,
          created_at: new Date().toISOString()
        };

        setCurrentScan(initialScan);
        setScanState('scanning');

        // Update toast
        toast.loading('Scanning in progress...', { id: toastId });

        // Start polling for results
        await pollForResults(response.scan_id, toastId);

      } catch (err) {
        toast.dismiss(toastId);
        throw err;
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start scan';
      setError(errorMessage);
      setScanState('failed');
      toast.error(errorMessage);
      console.error('Scan error:', err);
    }
  }, [defaultOptions]);

  /**
   * Poll for scan results
   */
  const pollForResults = useCallback(async (
    scanId: string,
    toastId: string
  ): Promise<void> => {
    let attempts = 0;
    const maxAttempts = 60; // 2 minutes with 2-second intervals
    const intervalMs = 2000;

    const poll = async (): Promise<void> => {
      try {
        attempts++;

        // Check if scan was cancelled
        if (abortControllerRef.current?.signal.aborted) {
          toast.dismiss(toastId);
          return;
        }

        // Get current scan results
        const result = await ScanAPI.getScanResults(scanId);
        setCurrentScan(result);

        // Update progress
        const progressPercentage = calculateProgress(result, attempts);
        setProgress(progressPercentage);

        // Update progress message
        const progressMessage = getProgressMessage(progressPercentage);
        toast.loading(progressMessage, { id: toastId });

        if (result.status === 'completed') {
          // Scan completed successfully
          setScanState('completed');
          setProgress(100);
          setCurrentScan(result);
          toast.success('Scan completed successfully!', { id: toastId });
          return;
        }

        if (result.status === 'failed') {
          // Scan failed
          const errorMessage = result.error_message || 'Scan failed';
          setError(errorMessage);
          setScanState('failed');
          toast.error(errorMessage, { id: toastId });
          return;
        }

        // Continue polling if scan is still running
        if (attempts < maxAttempts) {
          pollIntervalRef.current = setTimeout(poll, intervalMs);
        } else {
          // Timeout reached
          throw new Error('Scan timeout: Please try again');
        }

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Polling error';
        setError(errorMessage);
        setScanState('failed');
        toast.error(errorMessage, { id: toastId });
      }
    };

    // Start polling
    await poll();
  }, []);

  /**
   * Calculate progress percentage based on scan state
   */
  const calculateProgress = (result: ScanResult, attempts: number): number => {
    if (result.status === 'completed') {
      return 100;
    }

    if (result.status === 'failed') {
      return 0;
    }

    // Calculate progress based on attempts (max 60 attempts = 100%)
    const baseProgress = Math.min((attempts / 60) * 100, 90);

    // Add some logic based on scan state if available
    if (result.status === 'scanning') {
      return Math.min(baseProgress + 10, 95);
    }

    return baseProgress;
  };

  /**
   * Get progress message based on percentage
   */
  const getProgressMessage = (progress: number): string => {
    const messageIndex = Math.floor((progress / 100) * (progressMessages.length - 1));
    return progressMessages[Math.min(messageIndex, progressMessages.length - 1)];
  };

  /**
   * Cancel current scan
   */
  const cancelScan = useCallback((): void => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (pollIntervalRef.current) {
      clearTimeout(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    setScanState('idle');
    setProgress(0);
    setError(null);
    toast('Scan cancelled', { icon: 'ℹ️' });
  }, []);

  /**
   * Get scan results by ID
   */
  const getResults = useCallback(async (scanId: string): Promise<ScanResult | null> => {
    try {
      const result = await ScanAPI.getScanResults(scanId);
      setCurrentScan(result);
      setScanState(result.status);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get scan results';
      setError(errorMessage);
      toast.error(errorMessage);
      return null;
    }
  }, []);

  /**
   * Reset scan state
   */
  const resetScan = useCallback((): void => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    if (pollIntervalRef.current) {
      clearTimeout(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }

    setScanState('idle');
    setCurrentScan(null);
    setProgress(0);
    setError(null);
  }, []);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (pollIntervalRef.current) {
        clearTimeout(pollIntervalRef.current);
      }
    };
  }, []);

  return {
    scanState,
    currentScan,
    progress,
    error,
    startScan,
    cancelScan,
    getResults,
    resetScan
  };
};

/**
 * Hook for getting scan URL from current route
 */
export const useScanUrl = (): string | null => {
  // This would integrate with react-router if needed
  // For now, return null as a placeholder
  return null;
};

/**
 * Hook for managing scan history (future feature)
 */
export const useScanHistory = () => {
  const [history, setHistory] = useState<Partial<ScanResult>[]>([]);

  const loadHistory = useCallback(async (): Promise<void> => {
    try {
      const response = await ScanAPI.listScans();
      setHistory(response.scans);
    } catch (err) {
      console.error('Failed to load scan history:', err);
    }
  }, []);

  const clearHistory = useCallback((): void => {
    setHistory([]);
  }, []);

  return {
    history,
    loadHistory,
    clearHistory
  };
};

export default useScan;