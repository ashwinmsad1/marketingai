import React from 'react';
import { cn, createVariants } from '../../utils/cn';

const cardVariants = {
  variant: {
    default: 'bg-white border border-gray-200 shadow-sm',
    elevated: 'bg-white shadow-md border-0',
    outlined: 'bg-transparent border-2 border-gray-200 shadow-none',
    ghost: 'bg-transparent border-0 shadow-none',
  },
  size: {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  },
  radius: {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-lg',
    lg: 'rounded-xl',
    xl: 'rounded-2xl',
  },
} as const;

const getCardClasses = createVariants(
  'transition-all duration-200',
  cardVariants,
  {
    variant: 'default',
    size: 'md',
    radius: 'md',
  }
);

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: keyof typeof cardVariants.variant;
  size?: keyof typeof cardVariants.size;
  radius?: keyof typeof cardVariants.radius;
  hoverable?: boolean;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  variant,
  size,
  radius,
  hoverable = false,
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn(
        getCardClasses({ variant, size, radius }),
        hoverable && 'hover:shadow-md hover:border-gray-300 cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

// Card Header Component
interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn('pb-4 border-b border-gray-100 mb-4', className)}
      {...props}
    >
      {children}
    </div>
  );
};

// Card Content Component
interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardContent: React.FC<CardContentProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div className={cn('', className)} {...props}>
      {children}
    </div>
  );
};

// Card Footer Component
interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <div
      className={cn('pt-4 border-t border-gray-100 mt-4', className)}
      {...props}
    >
      {children}
    </div>
  );
};

// Card Title Component
interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

export const CardTitle: React.FC<CardTitleProps> = ({
  as: Component = 'h3',
  className,
  children,
  ...props
}) => {
  return (
    <Component
      className={cn('text-lg font-semibold text-gray-900', className)}
      {...props}
    >
      {children}
    </Component>
  );
};

// Card Description Component
interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export const CardDescription: React.FC<CardDescriptionProps> = ({
  className,
  children,
  ...props
}) => {
  return (
    <p
      className={cn('text-sm text-gray-600 mt-1', className)}
      {...props}
    >
      {children}
    </p>
  );
};

export default Card;