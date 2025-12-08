/**
 * Loading spinner component with various sizes and styles
 */
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  className?: string;
  label?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = '',
  label
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  const colorClasses = {
    primary: 'border-primary-500 border-t-transparent',
    secondary: 'border-text-tertiary border-t-transparent',
    success: 'border-success-500 border-t-transparent',
    warning: 'border-warning-500 border-t-transparent',
    danger: 'border-danger-500 border-t-transparent'
  };

  const containerClasses = `flex items-center justify-center ${className}`;

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center space-y-2">
        <div
          className={`
            spinner
            ${sizeClasses[size]}
            ${colorClasses[color]}
            border-2
            rounded-full
            animate-spin
          `}
          aria-hidden="true"
        />
        {label && (
          <span className="text-sm text-text-secondary animate-pulse">
            {label}
          </span>
        )}
      </div>
    </div>
  );
};

/**
 * Pulse loading indicator
 */
export const PulseLoader: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4'
  };

  return (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={`
            ${sizeClasses[size]}
            bg-primary-500
            rounded-full
            animate-pulse
          `}
          style={{
            animationDelay: `${i * 0.2}s`,
            animationDuration: '1.4s'
          }}
        />
      ))}
    </div>
  );
};

/**
 * Dots loading indicator
 */
export const DotsLoader: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'h-1 w-1',
    md: 'h-2 w-2',
    lg: 'h-3 w-3'
  };

  return (
    <div className={`flex space-x-1 ${className}`}>
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={`
            ${sizeClasses[size]}
            bg-primary-500
            rounded-full
            animate-bounce
          `}
          style={{
            animationDelay: `${i * 0.1}s`
          }}
        />
      ))}
    </div>
  );
};

/**
 * Skeleton loading component
 */
export const Skeleton: React.FC<{
  className?: string;
  variant?: 'text' | 'rectangular' | 'circular';
  width?: string | number;
  height?: string | number;
}> = ({
  className = '',
  variant = 'text',
  width,
  height
}) => {
  const variantClasses = {
    text: 'rounded',
    rectangular: 'rounded-md',
    circular: 'rounded-full'
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`
        bg-background-tertiary
        animate-pulse
        ${variantClasses[variant]}
        ${className}
      `}
      style={style}
    />
  );
};

/**
 * Progress bar component
 */
export const ProgressBar: React.FC<{
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'success' | 'warning' | 'danger';
  showLabel?: boolean;
  className?: string;
}> = ({
  value,
  max = 100,
  size = 'md',
  color = 'primary',
  showLabel = false,
  className = ''
}) => {
  const percentage = Math.min((value / max) * 100, 100);

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  const colorClasses = {
    primary: 'bg-primary-500',
    success: 'bg-success-500',
    warning: 'bg-warning-500',
    danger: 'bg-danger-500'
  };

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between text-sm text-text-secondary mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div
        className={`
          w-full
          bg-background-tertiary
          rounded-full
          overflow-hidden
          ${sizeClasses[size]}
        `}
      >
        <div
          className={`
            ${colorClasses[color]}
            h-full
            rounded-full
            transition-all
            duration-300
            ease-out
          `}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

/**
 * Full page loading overlay
 */
export const FullPageLoader: React.FC<{
  message?: string;
  showProgress?: boolean;
  progress?: number;
}> = ({ message = 'Loading...', showProgress = false, progress = 0 }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background bg-opacity-90 backdrop-blur-sm">
      <div className="flex flex-col items-center space-y-4 p-8 bg-background-secondary rounded-xl shadow-2xl">
        <LoadingSpinner size="xl" />
        <p className="text-lg font-medium text-text-primary">{message}</p>
        {showProgress && (
          <div className="w-64">
            <ProgressBar value={progress} showLabel />
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;