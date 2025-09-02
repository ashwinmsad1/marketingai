import React, { forwardRef } from 'react';
import { cn, createVariants } from '../../utils/cn';
import { Eye, EyeOff, AlertCircle, Check } from 'lucide-react';

const inputVariants = {
  size: {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-12 px-4 text-base',
  },
  variant: {
    default: 'border border-gray-300 bg-white focus:border-blue-500 focus:ring-blue-500',
    filled: 'border-0 bg-gray-100 focus:bg-white focus:ring-2 focus:ring-blue-500',
    flushed: 'border-0 border-b-2 border-gray-300 rounded-none px-0 focus:border-blue-500',
  },
  state: {
    default: '',
    error: 'border-red-500 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-500 focus:border-green-500 focus:ring-green-500',
    warning: 'border-amber-500 focus:border-amber-500 focus:ring-amber-500',
  },
} as const;

const getInputClasses = createVariants(
  'w-full rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed',
  inputVariants,
  {
    size: 'md',
    variant: 'default',
    state: 'default',
  }
);

interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  size?: keyof typeof inputVariants.size;
  variant?: keyof typeof inputVariants.variant;
  state?: keyof typeof inputVariants.state;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  label?: string;
  helperText?: string;
  errorText?: string;
  showPasswordToggle?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  size,
  variant,
  state,
  leftIcon,
  rightIcon,
  label,
  helperText,
  errorText,
  showPasswordToggle = false,
  className,
  type: initialType = 'text',
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [type, setType] = React.useState(initialType);

  React.useEffect(() => {
    if (showPasswordToggle && initialType === 'password') {
      setType(showPassword ? 'text' : 'password');
    }
  }, [showPassword, showPasswordToggle, initialType]);

  const currentState = errorText ? 'error' : state;
  const hasLeftIcon = leftIcon;
  const hasRightIcon = rightIcon || showPasswordToggle || currentState === 'success';

  const inputId = props.id || `input-${Math.random().toString(36).substring(2, 9)}`;

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      
      <div className="relative">
        {hasLeftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          type={type}
          className={cn(
            getInputClasses({ size, variant, state: currentState }),
            hasLeftIcon && 'pl-10',
            hasRightIcon && 'pr-10',
            className
          )}
          {...props}
        />
        
        {hasRightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
            {showPasswordToggle && initialType === 'password' && (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            )}
            
            {currentState === 'success' && (
              <Check className="w-4 h-4 text-green-500" />
            )}
            
            {currentState === 'error' && (
              <AlertCircle className="w-4 h-4 text-red-500" />
            )}
            
            {rightIcon && !showPasswordToggle && currentState === 'default' && (
              <span className="text-gray-500">{rightIcon}</span>
            )}
          </div>
        )}
      </div>
      
      {(helperText || errorText) && (
        <div className="mt-1">
          {errorText ? (
            <p className="text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errorText}
            </p>
          ) : (
            <p className="text-sm text-gray-500">{helperText}</p>
          )}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Textarea component
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  helperText?: string;
  errorText?: string;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(({
  label,
  helperText,
  errorText,
  resize = 'vertical',
  className,
  ...props
}, ref) => {
  const textareaId = props.id || `textarea-${Math.random().toString(36).substring(2, 9)}`;
  const hasError = Boolean(errorText);

  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize',
  };

  return (
    <div className="w-full">
      {label && (
        <label
          htmlFor={textareaId}
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          {label}
        </label>
      )}
      
      <textarea
        ref={ref}
        id={textareaId}
        className={cn(
          'w-full px-4 py-3 border rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed',
          hasError
            ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 bg-white focus:border-blue-500 focus:ring-blue-500',
          resizeClasses[resize],
          className
        )}
        {...props}
      />
      
      {(helperText || errorText) && (
        <div className="mt-1">
          {errorText ? (
            <p className="text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errorText}
            </p>
          ) : (
            <p className="text-sm text-gray-500">{helperText}</p>
          )}
        </div>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

export default Input;