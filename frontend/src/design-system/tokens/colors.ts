// Zoho-inspired color palette based on 2024 design research
export const colors = {
  // Primary colors - based on Zoho's signature blue
  primary: {
    50: '#f0f4ff',
    100: '#e0e9ff',
    200: '#c5d4ff',
    300: '#a1b6ff',
    400: '#7a8fff',
    500: '#5a6aff', // Primary brand color
    600: '#4c5bef',
    700: '#3d4ad9',
    800: '#333db3',
    900: '#2d3782',
  },

  // Secondary colors - Zoho's complementary orange/amber
  secondary: {
    50: '#fffbf0',
    100: '#fff5d9',
    200: '#ffeaa6',
    300: '#ffdd73',
    400: '#ffcf40',
    500: '#ffc107', // Secondary accent
    600: '#e6ad00',
    700: '#cc9900',
    800: '#b38600',
    900: '#997300',
  },

  // Success - Zoho's green palette
  success: {
    50: '#f0fff4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },

  // Warning - Amber/orange for notifications
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    200: '#fed7aa',
    300: '#fdba74',
    400: '#fb923c',
    500: '#f97316',
    600: '#ea580c',
    700: '#c2410c',
    800: '#9a3412',
    900: '#7c2d12',
  },

  // Error - Red palette
  error: {
    50: '#fef2f2',
    100: '#fee2e2',
    200: '#fecaca',
    300: '#fca5a5',
    400: '#f87171',
    500: '#ef4444',
    600: '#dc2626',
    700: '#b91c1c',
    800: '#991b1b',
    900: '#7f1d1d',
  },

  // Neutral colors - Zoho's clean grays
  neutral: {
    0: '#ffffff',
    50: '#fafafa',
    100: '#f5f5f5',
    150: '#ededed',
    200: '#e5e5e5',
    250: '#d4d4d4',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    850: '#1a202c',
    900: '#111827',
    950: '#030712',
  },

  // Blue-gray for Zoho's professional interface elements
  slate: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
  },
} as const;

// Semantic color mappings
export const semanticColors = {
  // Background colors
  background: {
    primary: colors.neutral[0],
    secondary: colors.neutral[50],
    tertiary: colors.neutral[100],
    sidebar: colors.slate[50],
    sidebarDark: colors.slate[800],
    card: colors.neutral[0],
    overlay: 'rgba(0, 0, 0, 0.5)',
  },

  // Text colors
  text: {
    primary: colors.neutral[900],
    secondary: colors.neutral[700],
    tertiary: colors.neutral[500],
    inverse: colors.neutral[0],
    muted: colors.neutral[400],
  },

  // Border colors
  border: {
    primary: colors.neutral[200],
    secondary: colors.neutral[150],
    focus: colors.primary[500],
    error: colors.error[500],
    success: colors.success[500],
  },

  // Interactive states
  interactive: {
    primary: colors.primary[500],
    primaryHover: colors.primary[600],
    primaryActive: colors.primary[700],
    secondary: colors.secondary[500],
    secondaryHover: colors.secondary[600],
    disabled: colors.neutral[300],
    disabledText: colors.neutral[500],
  },

  // Status colors
  status: {
    success: colors.success[500],
    warning: colors.warning[500],
    error: colors.error[500],
    info: colors.primary[500],
  },
} as const;

// Export utility functions for color manipulation
export const getColorValue = (colorPath: string): string => {
  const keys = colorPath.split('.');
  let result: any = { colors, semanticColors };
  
  for (const key of keys) {
    result = result[key];
    if (result === undefined) {
      console.warn(`Color path "${colorPath}" not found`);
      return '#000000';
    }
  }
  
  return result as string;
};

export type ColorTokens = typeof colors;
export type SemanticColors = typeof semanticColors;