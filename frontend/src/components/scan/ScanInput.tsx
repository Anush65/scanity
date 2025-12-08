/**
 * Scan input component with URL validation
 */
import React, { useState, useRef, useEffect } from 'react';
import { Globe, X, Check, AlertCircle } from 'lucide-react';
import { ScanInputProps } from '@/types';
import { validateUrl, sanitizeInput } from '@/utils/validation';

export const ScanInput: React.FC<ScanInputProps> = ({
  value,
  onChange,
  onSubmit,
  loading = false,
  error = null
}) => {
  const [focused, setFocused] = useState(false);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Validate URL on value change
  useEffect(() => {
    if (value.trim() === '') {
      setIsValid(null);
      return;
    }

    const validation = validateUrl(value);
    setIsValid(validation === null);
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const sanitizedValue = sanitizeInput(e.target.value);
    onChange(sanitizedValue);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    } else if (e.key === 'Escape') {
      onChange('');
    }
  };

  const handleSubmit = () => {
    if (!loading && value.trim()) {
      onSubmit();
    }
  };

  const handleClear = () => {
    onChange('');
    inputRef.current?.focus();
  };

  const getStatusIcon = () => {
    if (error) {
      return <AlertCircle className="h-5 w-5 text-danger-400" />;
    }
    if (isValid === true) {
      return <Check className="h-5 w-5 text-success-400" />;
    }
    if (isValid === false) {
      return <AlertCircle className="h-5 w-5 text-warning-400" />;
    }
    return <Globe className="h-5 w-5 text-text-tertiary" />;
  };

  const getInputClasses = () => {
    const baseClasses = 'input pr-24 transition-all duration-200';
    const focusClasses = focused ? 'ring-2 ring-primary-500 ring-offset-2 ring-offset-background' : '';
    const errorClasses = error ? 'border-danger-500 ring-danger-500' : '';
    const validClasses = isValid === true ? 'border-success-500' : '';

    return `${baseClasses} ${focusClasses} ${errorClasses} ${validClasses}`;
  };

  const getPlaceholderText = () => {
    if (focused) {
      return 'Enter a website URL...';
    }
    return 'https://example.com';
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="relative">
        {/* Main input */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            {getStatusIcon()}
          </div>

          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder={getPlaceholderText()}
            disabled={loading}
            className={getInputClasses()}
            spellCheck={false}
            autoComplete="off"
            aria-label="Website URL"
            aria-describedby={error ? 'url-error' : undefined}
            aria-invalid={!!error || isValid === false}
          />

          {/* Clear button */}
          {value && !loading && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute inset-y-0 right-16 flex items-center px-2 text-text-secondary hover:text-text-primary transition-colors"
              aria-label="Clear input"
            >
              <X className="h-4 w-4" />
            </button>
          )}

          {/* Scan button */}
          <div className="absolute inset-y-0 right-0 flex items-center pr-2">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading || !value.trim() || isValid === false}
              className="btn btn-primary h-10 px-4 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Start scan"
            >
              {loading ? 'Scanning...' : 'Scan Now'}
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mt-2 flex items-center space-x-2 text-sm text-danger-400 animate-fade-in">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span id="url-error">{error}</span>
          </div>
        )}

        {/* Validation hint */}
        {!error && value && isValid === false && (
          <div className="mt-2 text-sm text-warning-400 animate-fade-in">
            Please enter a valid URL (e.g., https://example.com)
          </div>
        )}

        {/* Success hint */}
        {!error && value && isValid === true && (
          <div className="mt-2 text-sm text-success-400 animate-fade-in">
            Valid URL - ready to scan!
          </div>
        )}
      </div>

      {/* Example URLs */}
      {!value && !error && (
        <div className="mt-4 text-center">
          <p className="text-sm text-text-tertiary mb-2">
            Try scanning these example sites:
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              'https://github.com',
              'https://stackoverflow.com',
              'https://wikipedia.org'
            ].map((url) => (
              <button
                key={url}
                type="button"
                onClick={() => onChange(url)}
                disabled={loading}
                className="text-sm text-primary-400 hover:text-primary-300 bg-background-tertiary hover:bg-background-secondary px-3 py-1 rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {url.replace('https://', '')}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center space-x-2 text-sm text-text-secondary">
            <div className="spinner h-4 w-4" />
            <span>Scanning in progress...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScanInput;