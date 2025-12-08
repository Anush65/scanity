/**
 * Animated scan button component
 */
import React, { useState } from 'react';
import { Search, Shield, Zap, Check, X, Loader } from 'lucide-react';
import { ScanButtonProps } from '@/types';

type ButtonState = 'default' | 'loading' | 'success' | 'error';

export const ScanButton: React.FC<ScanButtonProps> = ({
  onClick,
  loading = false,
  disabled = false
}) => {
  const [state, setState] = useState<ButtonState>('default');

  // Update state based on loading prop
  React.useEffect(() => {
    if (loading) {
      setState('loading');
    } else {
      setState('default');
    }
  }, [loading]);

  const handleClick = () => {
    if (!disabled && !loading) {
      setState('loading');
      onClick();
    }
  };

  const getStateIcon = () => {
    switch (state) {
      case 'loading':
        return <Loader className="h-5 w-5 animate-spin" />;
      case 'success':
        return <Check className="h-5 w-5" />;
      case 'error':
        return <X className="h-5 w-5" />;
      default:
        return <Search className="h-5 w-5" />;
    }
  };

  const getStateText = () => {
    switch (state) {
      case 'loading':
        return 'Scanning...';
      case 'success':
        return 'Complete!';
      case 'error':
        return 'Failed';
      default:
        return 'Scan Now';
    }
  };

  const getButtonClasses = () => {
    const baseClasses = 'btn btn-lg btn-primary relative overflow-hidden group transition-all duration-300';
    const stateClasses = {
      default: 'bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5',
      loading: 'bg-gradient-to-r from-primary-500 to-primary-600 cursor-wait',
      success: 'bg-gradient-to-r from-success-500 to-success-600 cursor-default',
      error: 'bg-gradient-to-r from-danger-500 to-danger-600 cursor-default'
    };

    const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed transform-none' : '';
    const loadingClasses = loading ? 'cursor-wait' : '';

    return `${baseClasses} ${stateClasses[state]} ${disabledClasses} ${loadingClasses}`;
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || loading}
      className={getButtonClasses()}
      aria-label={getStateText()}
      aria-busy={loading}
    >
      {/* Background animation overlay */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 transform -skew-x-12 -translate-x-full group-hover:translate-x-full transition-all duration-1000" />

      {/* Button content */}
      <div className="relative flex items-center justify-center space-x-2">
        <div className="transition-transform duration-200">
          {getStateIcon()}
        </div>

        <span className="font-semibold">
          {getStateText()}
        </span>
      </div>

      {/* Loading progress indicator */}
      {state === 'loading' && (
        <div className="absolute bottom-0 left-0 h-1 bg-white bg-opacity-30 animate-pulse-slow" />
      )}
    </button>
  );
};

/**
 * Alternative scan button with different styling
 */
export const ScanButtonAlt: React.FC<ScanButtonProps> = ({
  onClick,
  loading = false,
  disabled = false
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white transition-all duration-300 bg-gradient-to-r from-primary-500 to-accent hover:from-primary-600 hover:to-accent hover:shadow-glow rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500 to-accent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-300" />

      <div className="relative flex items-center space-x-3">
        {loading ? (
          <Loader className="h-6 w-6 animate-spin" />
        ) : (
          <Shield className="h-6 w-6 group-hover:rotate-12 transition-transform duration-300" />
        )}

        <span>{loading ? 'Scanning...' : 'Start Security Scan'}</span>

        {!loading && (
          <Zap className="h-5 w-5 opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-x-2 group-hover:translate-x-0" />
        )}
      </div>
    </button>
  );
};

/**
 * Minimal scan button
 */
export const ScanButtonMinimal: React.FC<ScanButtonProps> = ({
  onClick,
  loading = false,
  disabled = false
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="relative inline-flex items-center space-x-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-background"
    >
      {loading ? (
        <>
          <Loader className="h-4 w-4 animate-spin" />
          <span>Scanning...</span>
        </>
      ) : (
        <>
          <Search className="h-4 w-4" />
          <span>Scan</span>
        </>
      )}
    </button>
  );
};

export default ScanButton;