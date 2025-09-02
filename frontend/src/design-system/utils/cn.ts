import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility function to merge Tailwind CSS classes with clsx
 * This is the canonical way to handle conditional classes in our design system
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Create variant-based className utilities
 */
export type VariantProps<T> = {
  [K in keyof T]?: T[K] extends readonly (infer U)[]
    ? U extends string
      ? U
      : never
    : T[K] extends string
      ? T[K]
      : never;
};

/**
 * Create a component variant system
 */
export function createVariants<T extends Record<string, Record<string, string>>>(
  baseClasses: string,
  variants: T,
  defaultVariants?: Record<string, string>
) {
  return (props?: Record<string, any> & { className?: string }) => {
    const { className, ...variantProps } = props || {};
    
    const variantClasses = Object.entries(variantProps).map(([key, value]) => {
      const variantGroup = variants[key];
      if (variantGroup && value && variantGroup[value as string]) {
        return variantGroup[value as string];
      }
      return '';
    });

    const defaultClasses = defaultVariants
      ? Object.entries(defaultVariants).map(([key, value]) => {
          const variantGroup = variants[key];
          if (variantGroup && value && variantGroup[value as string] && !variantProps[key]) {
            return variantGroup[value as string];
          }
          return '';
        })
      : [];

    return cn(baseClasses, ...defaultClasses, ...variantClasses, className);
  };
}