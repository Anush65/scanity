/**
 * Custom hook for PDF export functionality
 */
import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { ScanAPI, APIUtils } from '@/services/api';
import { UsePDFExportReturn } from '@/types';

/**
 * Hook for managing PDF export operations
 */
export const usePDFExport = (): UsePDFExportReturn => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Export scan results as PDF
   */
  const exportPDF = useCallback(async (scanId: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      // Show loading toast
      const toastId = toast.loading('Generating PDF report...');

      try {
        // Download the PDF
        await ScanAPI.downloadPDF(scanId);

        // Show success toast
        toast.success('PDF report downloaded successfully!', { id: toastId });

      } catch (err) {
        toast.dismiss(toastId);
        throw err;
      }

    } catch (err) {
      const errorMessage = APIUtils.extractErrorMessage(err);
      setError(errorMessage);
      toast.error(errorMessage);
      console.error('PDF export error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Reset error state
   */
  const resetError = useCallback((): void => {
    setError(null);
  }, []);

  return {
    exportPDF,
    loading,
    error,
    resetError
  };
};

/**
 * Hook for managing multiple PDF exports
 */
export const useMultiplePDFExport = () => {
  const [exports, setExports] = useState<Map<string, boolean>>(new Map());
  const [errors, setErrors] = useState<Map<string, string>>(new Map());

  /**
   * Export multiple scans as PDFs
   */
  const exportMultiple = useCallback(async (scanIds: string[]): Promise<void> => {
    // Initialize export states
    const newExports = new Map<string, boolean>();
    const newErrors = new Map<string, string>();

    scanIds.forEach(scanId => {
      newExports.set(scanId, false);
    });

    setExports(newExports);
    setErrors(newErrors);

    // Export each scan
    const exportPromises = scanIds.map(async (scanId) => {
      try {
        newExports.set(scanId, true);
        setExports(new Map(newExports));

        await ScanAPI.downloadPDF(scanId);

        // Remove from exports map when complete
        newExports.delete(scanId);
        setExports(new Map(newExports));

        toast.success(`PDF exported for scan ${scanId.substring(0, 8)}...`);

      } catch (err) {
        const errorMessage = APIUtils.extractErrorMessage(err);
        newErrors.set(scanId, errorMessage);
        newExports.delete(scanId);

        setExports(new Map(newExports));
        setErrors(new Map(newErrors));

        toast.error(`Failed to export PDF for scan ${scanId.substring(0, 8)}...`);
      }
    });

    // Wait for all exports to complete
    await Promise.allSettled(exportPromises);
  }, []);

  /**
   * Check if a scan is currently being exported
   */
  const isExporting = useCallback((scanId: string): boolean => {
    return exports.get(scanId) || false;
  }, [exports]);

  /**
   * Get error for a specific scan
   */
  const getError = useCallback((scanId: string): string | null => {
    return errors.get(scanId) || null;
  }, [errors]);

  /**
   * Clear error for a specific scan
   */
  const clearError = useCallback((scanId: string): void => {
    const newErrors = new Map(errors);
    newErrors.delete(scanId);
    setErrors(newErrors);
  }, [errors]);

  /**
   * Clear all errors
   */
  const clearAllErrors = useCallback((): void => {
    setErrors(new Map());
  }, []);

  return {
    exportMultiple,
    isExporting,
    getError,
    clearError,
    clearAllErrors,
    exportingCount: exports.size,
    errors
  };
};

/**
 * Hook for PDF export configuration
 */
export const usePDFConfig = () => {
  const [includeScreenshots, setIncludeScreenshots] = useState<boolean>(true);
  const [includeDetailedFixes, setIncludeDetailedFixes] = useState<boolean>(true);
  const [pageSize, setPageSize] = useState<'A4' | 'Letter'>('A4');

  /**
   * Export configuration
   */
  const config = {
    includeScreenshots,
    includeDetailedFixes,
    pageSize
  };

  /**
   * Update configuration
   */
  const updateConfig = useCallback((updates: Partial<typeof config>) => {
    if (updates.includeScreenshots !== undefined) {
      setIncludeScreenshots(updates.includeScreenshots);
    }
    if (updates.includeDetailedFixes !== undefined) {
      setIncludeDetailedFixes(updates.includeDetailedFixes);
    }
    if (updates.pageSize !== undefined) {
      setPageSize(updates.pageSize);
    }
  }, []);

  /**
   * Reset to defaults
   */
  const resetConfig = useCallback(() => {
    setIncludeScreenshots(true);
    setIncludeDetailedFixes(true);
    setPageSize('A4');
  }, []);

  return {
    config,
    updateConfig,
    resetConfig
  };
};

export default usePDFExport;