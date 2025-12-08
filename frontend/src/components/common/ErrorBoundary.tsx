/**
 * Error Boundary component for catching and displaying React errors
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: Math.random().toString(36).substr(2, 9)
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to console in development
    if (import.meta.env.DEV) {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to external service in production
    if (import.meta.env.PROD) {
      // TODO: Add error logging service (Sentry, etc.)
      console.error('Production error:', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        errorId: this.state.errorId
      });
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-background flex items-center justify-center px-4">
          <div className="max-w-2xl w-full">
            <div className="text-center">
              {/* Error Icon */}
              <div className="flex justify-center mb-6">
                <div className="relative">
                  <div className="bg-danger-500 bg-opacity-20 rounded-full p-6">
                    <AlertTriangle className="h-12 w-12 text-danger-400" />
                  </div>
                  <div className="absolute -top-2 -right-2">
                    <Bug className="h-6 w-6 text-danger-400" />
                  </div>
                </div>
              </div>

              {/* Error Title */}
              <h1 className="text-4xl font-bold text-white mb-4">
                Oops! Something went wrong
              </h1>

              {/* Error Message */}
              <p className="text-lg text-text-secondary mb-8 max-w-md mx-auto">
                We encountered an unexpected error. Don't worry, our team has been notified and we're working on a fix.
              </p>

              {/* Error Details (Development Only) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="mb-8 text-left">
                  <details className="bg-background-secondary rounded-lg p-4 border border-background-tertiary">
                    <summary className="cursor-pointer text-sm font-mono text-text-secondary mb-2">
                      Error Details (Development)
                    </summary>
                    <div className="mt-2 space-y-2">
                      <div>
                        <span className="text-danger-400 font-semibold">Error:</span>
                        <pre className="text-xs text-text-tertiary mt-1 whitespace-pre-wrap">
                          {this.state.error.message}
                        </pre>
                      </div>
                      {this.state.error.stack && (
                        <div>
                          <span className="text-danger-400 font-semibold">Stack Trace:</span>
                          <pre className="text-xs text-text-tertiary mt-1 whitespace-pre-wrap">
                            {this.state.error.stack}
                          </pre>
                        </div>
                      )}
                      {this.state.errorId && (
                        <div>
                          <span className="text-danger-400 font-semibold">Error ID:</span>
                          <code className="text-xs text-text-tertiary bg-background-tertiary px-2 py-1 rounded">
                            {this.state.errorId}
                          </code>
                        </div>
                      )}
                    </div>
                  </details>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={this.handleRetry}
                  className="btn btn-primary inline-flex items-center space-x-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  <span>Try Again</span>
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="btn btn-secondary inline-flex items-center space-x-2"
                >
                  <Home className="h-4 w-4" />
                  <span>Go Home</span>
                </button>
              </div>

              {/* Support Info */}
              <div className="mt-8 text-center">
                <p className="text-sm text-text-tertiary">
                  If this problem persists, please{' '}
                  <a
                    href="mailto:support@scanity.com"
                    className="text-primary-400 hover:text-primary-300 transition-colors"
                  >
                    contact our support team
                  </a>
                  {this.state.errorId && (
                    <>
                      {' '}and reference error ID:{' '}
                      <code className="text-xs bg-background-tertiary px-2 py-1 rounded text-text-secondary">
                        {this.state.errorId}
                      </code>
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Simple error boundary for specific components
 */
export const SimpleErrorBoundary: React.FC<{
  children: ReactNode;
  fallback?: ReactNode;
}> = ({ children, fallback }) => {
  return (
    <ErrorBoundary
      fallback={
        fallback || (
          <div className="flex items-center justify-center p-8 bg-background-secondary rounded-lg border border-background-tertiary">
            <div className="text-center">
              <AlertTriangle className="h-8 w-8 text-danger-400 mx-auto mb-2" />
              <p className="text-text-secondary">Something went wrong</p>
            </div>
          </div>
        )
      }
    >
      {children}
    </ErrorBoundary>
  );
};

export default ErrorBoundary;