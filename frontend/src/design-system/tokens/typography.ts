// Zoho-inspired typography system
export const fontFamilies = {
  sans: [
    'Inter',
    'SF Pro Display',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'Helvetica Neue',
    'Arial',
    'sans-serif',
  ].join(', '),
  mono: [
    'SF Mono',
    'Monaco',
    'Inconsolata',
    'Roboto Mono',
    'Courier New',
    'monospace',
  ].join(', '),
} as const;

export const fontSizes = {
  xs: '0.75rem',    // 12px
  sm: '0.875rem',   // 14px
  base: '1rem',     // 16px
  lg: '1.125rem',   // 18px
  xl: '1.25rem',    // 20px
  '2xl': '1.5rem',  // 24px
  '3xl': '1.875rem', // 30px
  '4xl': '2.25rem', // 36px
  '5xl': '3rem',    // 48px
  '6xl': '3.75rem', // 60px
  '7xl': '4.5rem',  // 72px
  '8xl': '6rem',    // 96px
  '9xl': '8rem',    // 128px
} as const;

export const fontWeights = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',
} as const;

export const lineHeights = {
  none: '1',
  tight: '1.25',
  snug: '1.375',
  normal: '1.5',
  relaxed: '1.625',
  loose: '2',
} as const;

export const letterSpacing = {
  tighter: '-0.05em',
  tight: '-0.025em',
  normal: '0em',
  wide: '0.025em',
  wider: '0.05em',
  widest: '0.1em',
} as const;

// Typography presets following Zoho's hierarchy
export const typography = {
  // Display text - for hero sections and major headings
  display: {
    '2xl': {
      fontSize: fontSizes['7xl'],
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.none,
      letterSpacing: letterSpacing.tight,
    },
    xl: {
      fontSize: fontSizes['6xl'],
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.none,
      letterSpacing: letterSpacing.tight,
    },
    lg: {
      fontSize: fontSizes['5xl'],
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.tight,
      letterSpacing: letterSpacing.tight,
    },
    md: {
      fontSize: fontSizes['4xl'],
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.tight,
    },
    sm: {
      fontSize: fontSizes['3xl'],
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.tight,
    },
  },

  // Headings - for section titles
  heading: {
    h1: {
      fontSize: fontSizes['2xl'],
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.tight,
    },
    h2: {
      fontSize: fontSizes.xl,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.tight,
    },
    h3: {
      fontSize: fontSizes.lg,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.snug,
    },
    h4: {
      fontSize: fontSizes.base,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.snug,
    },
    h5: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.normal,
    },
    h6: {
      fontSize: fontSizes.xs,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.normal,
      letterSpacing: letterSpacing.wide,
      textTransform: 'uppercase' as const,
    },
  },

  // Body text
  body: {
    lg: {
      fontSize: fontSizes.lg,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.relaxed,
    },
    md: {
      fontSize: fontSizes.base,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.normal,
    },
    sm: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.normal,
    },
    xs: {
      fontSize: fontSizes.xs,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.tight,
    },
  },

  // UI text - for interface elements
  ui: {
    button: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.none,
    },
    buttonLarge: {
      fontSize: fontSizes.base,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.none,
    },
    label: {
      fontSize: fontSizes.sm,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.normal,
    },
    caption: {
      fontSize: fontSizes.xs,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.normal,
    },
    overline: {
      fontSize: fontSizes.xs,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.tight,
      letterSpacing: letterSpacing.wider,
      textTransform: 'uppercase' as const,
    },
  },

  // Code and monospace
  code: {
    inline: {
      fontSize: fontSizes.sm,
      fontFamily: fontFamilies.mono,
      fontWeight: fontWeights.normal,
    },
    block: {
      fontSize: fontSizes.sm,
      fontFamily: fontFamilies.mono,
      fontWeight: fontWeights.normal,
      lineHeight: lineHeights.relaxed,
    },
  },
} as const;

// Utility type for accessing typography styles
export type TypographyStyle = {
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
  letterSpacing?: string;
  fontFamily?: string;
  textTransform?: 'uppercase' | 'lowercase' | 'capitalize' | 'none';
};

export type Typography = typeof typography;
export type FontSizes = typeof fontSizes;
export type FontWeights = typeof fontWeights;
export type LineHeights = typeof lineHeights;