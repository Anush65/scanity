/**
 * Validation utilities for the Scanity frontend
 */
import { ValidationError } from '@/types';

/**
 * URL validation regex pattern
 */
const URL_REGEX = /^https?:\/\/(?:[-\w.])+(?:\:[0-9]+)?(?:\/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$/;

/**
 * Validates a URL for scanning
 */
export const validateUrl = (url: string): ValidationError | null => {
  if (!url) {
    return {
      field: 'url',
      message: 'URL is required'
    };
  }

  if (url.length > 255) {
    return {
      field: 'url',
      message: 'URL is too long (maximum 255 characters)'
    };
  }

  if (!URL_REGEX.test(url)) {
    return {
      field: 'url',
      message: 'Please enter a valid URL (e.g., https://example.com)'
    };
  }

  // Check for blocked domains
  const blockedDomains = ['localhost', '127.0.0.1'];
  const urlObj = new URL(url);

  if (blockedDomains.includes(urlObj.hostname)) {
    return {
      field: 'url',
      message: 'This domain cannot be scanned'
    };
  }

  return null;
};

/**
 * Validates scan options
 */
export const validateScanOptions = (options: any): ValidationError[] => {
  const errors: ValidationError[] = [];

  if (!options) {
    return errors;
  }

  // Validate scan depth
  if (options.scan_depth && !['quick', 'standard', 'deep'].includes(options.scan_depth)) {
    errors.push({
      field: 'scan_depth',
      message: 'Invalid scan depth. Must be quick, standard, or deep'
    });
  }

  return errors;
};

/**
 * General form validation
 */
export const validateField = (value: string, rules: ValidationRules): ValidationError | null => {
  if (rules.required && (!value || value.trim() === '')) {
    return {
      field: rules.field || 'field',
      message: rules.requiredMessage || `${rules.field || 'Field'} is required`
    };
  }

  if (rules.minLength && value.length < rules.minLength) {
    return {
      field: rules.field || 'field',
      message: rules.minLengthMessage || `Must be at least ${rules.minLength} characters`
    };
  }

  if (rules.maxLength && value.length > rules.maxLength) {
    return {
      field: rules.field || 'field',
      message: rules.maxLengthMessage || `Must be no more than ${rules.maxLength} characters`
    };
  }

  if (rules.pattern && !rules.pattern.test(value)) {
    return {
      field: rules.field || 'field',
      message: rules.patternMessage || 'Invalid format'
    };
  }

  if (rules.custom && !rules.custom(value)) {
    return {
      field: rules.field || 'field',
      message: rules.customMessage || 'Invalid value'
    };
  }

  return null;
};

/**
 * Validation rules interface
 */
export interface ValidationRules {
  field?: string;
  required?: boolean;
  requiredMessage?: string;
  minLength?: number;
  minLengthMessage?: string;
  maxLength?: number;
  maxLengthMessage?: string;
  pattern?: RegExp;
  patternMessage?: string;
  custom?: (value: string) => boolean;
  customMessage?: string;
}

/**
 * Sanitizes user input for security
 */
export const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove scripts
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, ''); // Remove event handlers
};

/**
 * Validates that a string is safe for display
 */
export const isSafeString = (input: string): boolean => {
  // Check for potentially dangerous patterns
  const dangerousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
  ];

  return !dangerousPatterns.some(pattern => pattern.test(input));
};

/**
 * Validates scan progress percentage
 */
export const validateProgress = (progress: number): boolean => {
  return progress >= 0 && progress <= 100;
};

/**
 * Validates health score
 */
export const validateHealthScore = (score: number): boolean => {
  return score >= 0 && score <= 100;
};

/**
 * Validates issue severity
 */
export const validateSeverity = (severity: string): boolean => {
  return ['HIGH', 'MEDIUM', 'LOW'].includes(severity);
};

/**
 * Validates issue category
 */
export const validateCategory = (category: string): boolean => {
  return ['security', 'performance', 'quality'].includes(category);
};

/**
 * Validates scan ID format (UUID)
 */
export const validateScanId = (scanId: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(scanId);
};

/**
 * Validates file size for uploads (future feature)
 */
export const validateFileSize = (size: number, maxSize: number): boolean => {
  return size <= maxSize;
};

/**
 * Validates file type for uploads (future feature)
 */
export const validateFileType = (type: string, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(type);
};