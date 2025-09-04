import React from 'react';
import { Loader2, AlertCircle, CheckCircle2, RefreshCcw } from 'lucide-react';
import { Button } from '../design-system';

// Loading spinner component
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <Loader2 
      className={`animate-spin text-blue-600 ${sizeClasses[size]} ${className}`} 
    />
  );
};

// Full page loading overlay
interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  children?: React.ReactNode;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  isLoading, 
  message = 'Loading...', 
  children 
}) => {
  if (!isLoading) {
    return <>{children}</>;
  }

  return (
    <div className="relative">
      {children && <div className="opacity-50 pointer-events-none">{children}</div>}
      <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50">
        <div className="flex flex-col items-center space-y-3">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 font-medium">{message}</p>
        </div>
      </div>
    </div>
  );
};

// Skeleton loading component
interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  animated?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  width = '100%', 
  height = '1rem', 
  className = '',
  animated = true 
}) => {
  const widthStyle = typeof width === 'number' ? `${width}px` : width;
  const heightStyle = typeof height === 'number' ? `${height}px` : height;

  return (
    <div 
      className={`bg-gray-200 rounded ${animated ? 'animate-pulse' : ''} ${className}`}
      style={{ width: widthStyle, height: heightStyle }}
    />
  );
};

// Card skeleton for loading states
export const CardSkeleton: React.FC = () => (
  <div className="bg-white p-6 rounded-lg shadow border animate-pulse">
    <div className="flex items-center space-x-4 mb-4">
      <Skeleton width={48} height={48} className="rounded-full" />
      <div className="flex-1">
        <Skeleton height={20} className="mb-2" />
        <Skeleton height={16} width="60%" />
      </div>
    </div>
    <Skeleton height={16} className="mb-2" />
    <Skeleton height={16} width="80%" />
  </div>
);

// Table skeleton for loading states
interface TableSkeletonProps {
  rows?: number;
  columns?: number;
}

export const TableSkeleton: React.FC<TableSkeletonProps> = ({ 
  rows = 5, 
  columns = 4 
}) => (
  <div className="bg-white rounded-lg shadow overflow-hidden">
    <div className="p-4 border-b border-gray-200">
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} height={20} />
        ))}
      </div>
    </div>
    {Array.from({ length: rows }).map((_, rowIndex) => (
      <div key={rowIndex} className="p-4 border-b border-gray-100 last:border-b-0">
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} height={16} />
          ))}
        </div>
      </div>
    ))}
  </div>
);

// Async operation state component
interface AsyncOperationProps {
  isLoading: boolean;
  error?: string | null;
  success?: boolean;
  children: React.ReactNode;
  onRetry?: () => void;
  loadingMessage?: string;
  errorMessage?: string;
  successMessage?: string;
}

export const AsyncOperation: React.FC<AsyncOperationProps> = ({
  isLoading,
  error,
  success,
  children,
  onRetry,
  loadingMessage = 'Loading...',
  errorMessage,
  successMessage,
}) => {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="flex flex-col items-center space-y-3">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600 font-medium">{loadingMessage}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Something went wrong
          </h3>
          <p className="text-gray-600 mb-4">
            {errorMessage || error}
          </p>
          {onRetry && (
            <Button
              onClick={onRetry}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <RefreshCcw className="w-4 h-4" />
              <span>Try Again</span>
            </Button>
          )}
        </div>
      </div>
    );
  }

  if (success && successMessage) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
          <p className="text-green-600 font-medium">{successMessage}</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

// Button loading state wrapper
interface ButtonLoadingProps {
  isLoading: boolean;
  loadingText?: string;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  variant?: 'primary' | 'secondary' | 'outline';
}

export const ButtonWithLoading: React.FC<ButtonLoadingProps> = ({
  isLoading,
  loadingText = 'Loading...',
  children,
  disabled,
  onClick,
  className,
  variant = 'primary',
}) => {
  return (
    <Button
      onClick={onClick}
      disabled={isLoading || disabled}
      className={`flex items-center space-x-2 ${className}`}
      variant={variant}
    >
      {isLoading && <LoadingSpinner size="sm" />}
      <span>{isLoading ? loadingText : children}</span>
    </Button>
  );
};

// Hook for managing loading states
export interface UseLoadingState {
  isLoading: boolean;
  error: string | null;
  success: boolean;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSuccess: (success: boolean) => void;
  reset: () => void;
  executeAsync: <T>(
    asyncFn: () => Promise<T>,
    successMessage?: string
  ) => Promise<T | null>;
}

export const useLoadingState = (): UseLoadingState => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);

  const setLoading = React.useCallback((loading: boolean) => {
    setIsLoading(loading);
    if (loading) {
      setError(null);
      setSuccess(false);
    }
  }, []);

  const setErrorState = React.useCallback((errorMessage: string | null) => {
    setError(errorMessage);
    setIsLoading(false);
    setSuccess(false);
  }, []);

  const setSuccessState = React.useCallback((successState: boolean) => {
    setSuccess(successState);
    if (successState) {
      setError(null);
      setIsLoading(false);
    }
  }, []);

  const reset = React.useCallback(() => {
    setIsLoading(false);
    setError(null);
    setSuccess(false);
  }, []);

  const executeAsync = React.useCallback(async <T,>(
    asyncFn: () => Promise<T>,
    successMessage?: string
  ): Promise<T | null> => {
    try {
      setLoading(true);
      const result = await asyncFn();
      if (successMessage) {
        setSuccessState(true);
      } else {
        setIsLoading(false);
      }
      return result;
    } catch (err: any) {
      setErrorState(err.message || 'An error occurred');
      return null;
    }
  }, [setLoading, setErrorState, setSuccessState]);

  return {
    isLoading,
    error,
    success,
    setLoading,
    setError: setErrorState,
    setSuccess: setSuccessState,
    reset,
    executeAsync,
  };
};

export default {
  LoadingSpinner,
  LoadingOverlay,
  Skeleton,
  CardSkeleton,
  TableSkeleton,
  AsyncOperation,
  ButtonWithLoading,
  useLoadingState,
};