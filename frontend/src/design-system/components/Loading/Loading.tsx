import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  return (
    <Loader2 
      className={cn(
        'animate-spin text-blue-600',
        sizeClasses[size],
        className
      )} 
    />
  );
};

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  text?: string;
  className?: string;
  overlay?: boolean;
  fullScreen?: boolean;
}

export const Loading: React.FC<LoadingProps> = ({ 
  size = 'md',
  text,
  className,
  overlay = false,
  fullScreen = false,
}) => {
  const content = (
    <div className={cn(
      'flex flex-col items-center justify-center space-y-3',
      fullScreen && 'min-h-screen',
      !fullScreen && 'p-8',
      className
    )}>
      <LoadingSpinner size={size} />
      {text && (
        <p className="text-sm text-gray-600 animate-pulse">
          {text}
        </p>
      )}
    </div>
  );

  if (overlay) {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-80 backdrop-blur-sm z-50 flex items-center justify-center">
        {content}
      </div>
    );
  }

  return content;
};

// Skeleton loading components
interface SkeletonProps {
  className?: string;
  width?: string;
  height?: string;
  rounded?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({ 
  className,
  width,
  height,
  rounded = false,
}) => {
  return (
    <div 
      className={cn(
        'animate-pulse bg-gray-200',
        rounded ? 'rounded-full' : 'rounded-md',
        className
      )}
      style={{
        width: width || '100%',
        height: height || '1rem',
      }}
    />
  );
};

// Card skeleton
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('p-6 bg-white border border-gray-200 rounded-lg shadow-sm', className)}>
      <div className="space-y-4">
        <div className="flex items-center space-x-3">
          <Skeleton width="40px" height="40px" rounded />
          <div className="space-y-2 flex-1">
            <Skeleton width="60%" height="16px" />
            <Skeleton width="40%" height="14px" />
          </div>
        </div>
        <div className="space-y-2">
          <Skeleton width="100%" height="14px" />
          <Skeleton width="80%" height="14px" />
          <Skeleton width="90%" height="14px" />
        </div>
        <div className="flex justify-between items-center pt-2">
          <Skeleton width="80px" height="32px" />
          <Skeleton width="100px" height="32px" />
        </div>
      </div>
    </div>
  );
};

// Table skeleton
export const TableSkeleton: React.FC<{ 
  rows?: number; 
  columns?: number; 
  className?: string;
}> = ({ 
  rows = 5, 
  columns = 4, 
  className 
}) => {
  return (
    <div className={cn('bg-white border border-gray-200 rounded-lg overflow-hidden', className)}>
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex space-x-4">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={i} width="120px" height="20px" />
          ))}
        </div>
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="border-b border-gray-100 p-4">
          <div className="flex space-x-4">
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton 
                key={colIndex} 
                width={colIndex === 0 ? '150px' : '100px'} 
                height="16px" 
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// List skeleton
export const ListSkeleton: React.FC<{ 
  items?: number; 
  className?: string;
}> = ({ 
  items = 5, 
  className 
}) => {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="flex items-center space-x-3 p-3 bg-white border border-gray-200 rounded-lg">
          <Skeleton width="48px" height="48px" rounded />
          <div className="space-y-2 flex-1">
            <Skeleton width="70%" height="16px" />
            <Skeleton width="50%" height="14px" />
          </div>
          <Skeleton width="80px" height="32px" />
        </div>
      ))}
    </div>
  );
};

// Page skeleton
export const PageSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="space-y-3">
        <Skeleton width="200px" height="32px" />
        <Skeleton width="400px" height="16px" />
      </div>
      
      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Array.from({ length: 3 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
      
      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TableSkeleton />
        </div>
        <div>
          <ListSkeleton />
        </div>
      </div>
    </div>
  );
};

export { LoadingSpinner };
export default Loading;