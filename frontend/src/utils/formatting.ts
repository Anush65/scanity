/**
 * Formatting utilities for the Scanity frontend
 */
import { IssueCategory, IssueSeverity } from '@/types';

/**
 * Formats duration in seconds to human readable string
 */
export const formatDuration = (seconds: number): string => {
  if (seconds < 1) {
    return `${Math.round(seconds * 1000)}ms`;
  } else if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  } else {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  }
};

/**
 * Formats file size in KB to human readable string
 */
export const formatFileSize = (sizeKb: number): string => {
  if (sizeKb < 1024) {
    return `${sizeKb}KB`;
  } else if (sizeKb < 1024 * 1024) {
    return `${(sizeKb / 1024).toFixed(1)}MB`;
  } else {
    return `${(sizeKb / (1024 * 1024)).toFixed(1)}GB`;
  }
};

/**
 * Formats a timestamp to relative time
 */
export const formatRelativeTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) {
    return 'just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString();
  }
};

/**
 * Formats a timestamp to a readable date string
 */
export const formatDate = (timestamp: string, options?: Intl.DateTimeFormatOptions): string => {
  const date = new Date(timestamp);
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };

  return date.toLocaleDateString(undefined, options || defaultOptions);
};

/**
 * Truncates text and adds ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Capitalizes the first letter of a string
 */
export const capitalize = (text: string): string => {
  if (!text) return text;
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Converts snake_case or kebab-case to Title Case
 */
export const toTitleCase = (text: string): string => {
  return text
    .replace(/[_-]/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Formats category name for display
 */
export const formatCategory = (category: IssueCategory): string => {
  const categoryNames: Record<IssueCategory, string> = {
    security: 'Security',
    performance: 'Performance',
    quality: 'Code Quality'
  };
  return categoryNames[category] || category;
};

/**
 * Formats severity name for display
 */
export const formatSeverity = (severity: IssueSeverity): string => {
  return capitalize(severity.toLowerCase());
};

/**
 * Gets color class for health score
 */
export const getHealthScoreColor = (score: number): string => {
  if (score >= 90) {
    return 'text-success-500';
  } else if (score >= 70) {
    return 'text-warning-500';
  } else {
    return 'text-danger-500';
  }
};

/**
 * Gets color class for severity
 */
export const getSeverityColor = (severity: IssueSeverity): string => {
  switch (severity) {
    case 'HIGH':
      return 'severity-high';
    case 'MEDIUM':
      return 'severity-medium';
    case 'LOW':
      return 'severity-low';
    default:
      return 'severity-low';
  }
};

/**
 * Gets category color class
 */
export const getCategoryColor = (category: IssueCategory): string => {
  switch (category) {
    case 'security':
      return 'text-danger-400';
    case 'performance':
      return 'text-warning-400';
    case 'quality':
      return 'text-primary-400';
    default:
      return 'text-text-secondary';
  }
};

/**
 * Gets background color class for category
 */
export const getCategoryBgColor = (category: IssueCategory): string => {
  switch (category) {
    case 'security':
      return 'bg-danger-500 bg-opacity-10 border-danger-500 border-opacity-30';
    case 'performance':
      return 'bg-warning-500 bg-opacity-10 border-warning-500 border-opacity-30';
    case 'quality':
      return 'bg-primary-500 bg-opacity-10 border-primary-500 border-opacity-30';
    default:
      return 'bg-background-tertiary border-background-tertiary';
  }
};

/**
 * Formats scan status for display
 */
export const formatScanStatus = (status: string): string => {
  const statusMap: Record<string, string> = {
    pending: 'Initializing...',
    scanning: 'Scanning...',
    completed: 'Completed',
    failed: 'Failed'
  };
  return statusMap[status] || status;
};

/**
 * Gets status color class
 */
export const getScanStatusColor = (status: string): string => {
  switch (status) {
    case 'completed':
      return 'text-success-400';
    case 'failed':
      return 'text-danger-400';
    case 'scanning':
      return 'text-primary-400';
    default:
      return 'text-text-secondary';
  }
};

/**
 * Formats percentage for display
 */
export const formatPercentage = (value: number, decimals: number = 0): string => {
  return `${value.toFixed(decimals)}%`;
};

/**
 * Formats number with locale-specific formatting
 */
export const formatNumber = (value: number): string => {
  return new Intl.NumberFormat().format(value);
};

/**
 * Formats currency (future use)
 */
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

/**
 * Pluralizes words based on count
 */
export const pluralize = (word: string, count: number, pluralWord?: string): string => {
  if (count === 1) {
    return word;
  }
  return pluralWord || `${word}s`;
};

/**
 * Converts camelCase to kebab-case
 */
export const camelToKebab = (str: string): string => {
  return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
};

/**
 * Converts kebab-case to camelCase
 */
export const kebabToCamel = (str: string): string => {
  return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
};

/**
 * Debounce function for limiting function calls
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Throttle function for limiting function calls
 */
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * Generates a random ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Deep clones an object
 */
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Checks if a value is empty (null, undefined, empty string, empty array, empty object)
 */
export const isEmpty = (value: any): boolean => {
  if (value == null) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
};

/**
 * Removes HTML tags from a string
 */
export const stripHtml = (html: string): string => {
  return html.replace(/<[^>]*>/g, '');
};

/**
 * Escapes HTML to prevent XSS
 */
export const escapeHtml = (text: string): string => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};