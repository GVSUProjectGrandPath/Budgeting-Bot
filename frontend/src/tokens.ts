/**
 * Design Token Export for Brand Unification
 * 
 * This module exports the complete design token map used by the PGPBOT frontend.
 * It can be imported by marketing sites or other applications to maintain
 * consistent branding across all touchpoints.
 * 
 * Usage:
 * import { tokens, applyTokens } from './tokens';
 * applyTokens('light'); // Apply light theme
 * applyTokens('dark');  // Apply dark theme
 */

export interface ThemeTokens {
  // Surface colors
  surface0: string;
  surface1: string;
  
  // Header colors
  headerBg: string;
  headerText: string;
  
  // Bubble colors
  bubbleUser: string;
  bubbleBot: string;
  
  // Interactive elements
  chipBg: string;
  chipText: string;
  
  // Structural elements
  outline: string;
  progress: string;
  
  // Input elements
  inputBg: string;
  inputText: string;
  
  // Status indicators
  statusDot: string;
  iconStroke: string;
  
  // Index signature for compatibility
  [key: string]: string;
}

export interface LayoutTokens {
  containerMaxWidth: string;
  chatWidth: string;
  sidebarWidth: string;
  gapColumns: string;
  borderRadiusPanel: string;
  borderRadiusBubble: string;
  borderRadiusChip: string;
  outlineWidth: string;
  
  // Index signature for compatibility
  [key: string]: string;
}

export interface TypographyTokens {
  fontFamily: string;
  fontSizeHeader: string;
  fontWeightHeader: string;
  fontSizeBody: string;
  fontWeightBody: string;
  lineHeightBody: string;
  fontSizeChip: string;
  fontWeightChip: string;
  
  // Index signature for compatibility
  [key: string]: string;
}

export interface SizingTokens {
  headerHeight: string;
  chipHeight: string;
  chipPadding: string;
  bubblePadding: string;
  bubbleMaxWidth: string;
  sidebarPadding: string;
  sidebarGap: string;
  composerHeight: string;
  inputPadding: string;
  iconSize: string;
  iconStrokeWidth: string;
  statusSize: string;
  
  // Index signature for compatibility
  [key: string]: string;
}

export interface DesignTokens {
  light: ThemeTokens;
  dark: ThemeTokens;
  layout: LayoutTokens;
  typography: TypographyTokens;
  sizing: SizingTokens;
}

/**
 * Complete design token map
 */
export const tokens: DesignTokens = {
  light: {
    surface0: '#FDF6E5',
    surface1: '#C6E7FA',
    headerBg: '#FEDB00',
    headerText: '#000',
    bubbleUser: '#A52C87',
    bubbleBot: '#44B59D',
    chipBg: '#7E66C1',
    chipText: '#fff',
    outline: '#603D20',
    progress: '#FF4F9B',
    inputBg: '#EDE3FF',
    inputText: '#000',
    statusDot: '#44B59D',
    iconStroke: '#218072',
  },
  dark: {
    surface0: '#0F1420',
    surface1: '#084C5E',
    headerBg: '#1B2545',
    headerText: '#E8F6F8',
    bubbleUser: '#7439C4',
    bubbleBot: '#44B59D',
    chipBg: '#5B43A9',
    chipText: '#fff',
    outline: '#44B59D',
    progress: '#1AE9F0',
    inputBg: '#242B3C',
    inputText: '#E8F6F8',
    statusDot: '#1AE9F0',
    iconStroke: '#1AE9F0',
  },
  layout: {
    containerMaxWidth: '960px',
    chatWidth: '66%',
    sidebarWidth: '34%',
    gapColumns: '24px',
    borderRadiusPanel: '16px',
    borderRadiusBubble: '24px',
    borderRadiusChip: '12px',
    outlineWidth: '1px',
  },
  typography: {
    fontFamily: '"Inter", sans-serif',
    fontSizeHeader: '20px',
    fontWeightHeader: '700',
    fontSizeBody: '16px',
    fontWeightBody: '400',
    lineHeightBody: '1.5',
    fontSizeChip: '14px',
    fontWeightChip: '600',
  },
  sizing: {
    headerHeight: '64px',
    chipHeight: '44px',
    chipPadding: '0 16px',
    bubblePadding: '14px 20px',
    bubbleMaxWidth: '70%',
    sidebarPadding: '20px',
    sidebarGap: '12px',
    composerHeight: '72px',
    inputPadding: '12px 16px',
    iconSize: '24px',
    iconStrokeWidth: '1.5px',
    statusSize: '12px',
  },
};

/**
 * Convert token object to CSS custom properties
 */
function tokensToCSSProperties(tokenObj: Record<string, string>, prefix = ''): Record<string, string> {
  const cssProps: Record<string, string> = {};
  
  Object.entries(tokenObj).forEach(([key, value]) => {
    // Convert camelCase to kebab-case
    const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    const propName = prefix ? `--${prefix}-${cssKey}` : `--${cssKey}`;
    cssProps[propName] = value;
  });
  
  return cssProps;
}

/**
 * Apply design tokens to the document
 * @param theme - 'light' or 'dark'
 * @param includeLayout - Whether to include layout tokens (default: true)
 */
export function applyTokens(
  theme: 'light' | 'dark' = 'light', 
  includeLayout = true
): void {
  const root = document.documentElement;
  
  // Apply theme tokens
  const themeProps = tokensToCSSProperties(tokens[theme]);
  Object.entries(themeProps).forEach(([prop, value]) => {
    root.style.setProperty(prop, value);
  });
  
  if (includeLayout) {
    // Apply layout tokens
    const layoutProps = tokensToCSSProperties(tokens.layout);
    Object.entries(layoutProps).forEach(([prop, value]) => {
      root.style.setProperty(prop, value);
    });
    
    // Apply typography tokens
    const typographyProps = tokensToCSSProperties(tokens.typography);
    Object.entries(typographyProps).forEach(([prop, value]) => {
      root.style.setProperty(prop, value);
    });
    
    // Apply sizing tokens
    const sizingProps = tokensToCSSProperties(tokens.sizing);
    Object.entries(sizingProps).forEach(([prop, value]) => {
      root.style.setProperty(prop, value);
    });
  }
  
  // Set data-theme attribute
  root.setAttribute('data-theme', theme);
}

/**
 * Get CSS string for embedding in marketing sites
 * @param theme - 'light' or 'dark'
 * @returns CSS string with all token definitions
 */
export function getTokensCSS(theme: 'light' | 'dark' = 'light'): string {
  const themeProps = tokensToCSSProperties(tokens[theme]);
  const layoutProps = tokensToCSSProperties(tokens.layout);
  const typographyProps = tokensToCSSProperties(tokens.typography);
  const sizingProps = tokensToCSSProperties(tokens.sizing);
  
  const allProps = { ...themeProps, ...layoutProps, ...typographyProps, ...sizingProps };
  
  const cssDeclarations = Object.entries(allProps)
    .map(([prop, value]) => `  ${prop}: ${value};`)
    .join('\n');
  
  return `:root {\n${cssDeclarations}\n}`;
}

/**
 * Color contrast checker for accessibility
 */
export function checkContrast(foreground: string, background: string): number {
  // This is a simplified contrast calculation
  // In production, use a proper color contrast library
  const getForegroundLuminance = (color: string): number => {
    // Simplified luminance calculation
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16) / 255;
    const g = parseInt(hex.substr(2, 2), 16) / 255;
    const b = parseInt(hex.substr(4, 2), 16) / 255;
    
    return 0.299 * r + 0.587 * g + 0.114 * b;
  };
  
  const foregroundLum = getForegroundLuminance(foreground);
  const backgroundLum = getForegroundLuminance(background);
  
  const lighter = Math.max(foregroundLum, backgroundLum);
  const darker = Math.min(foregroundLum, backgroundLum);
  
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Validate WCAG AA compliance for all token combinations
 */
export function validateAccessibility(): { theme: string; passes: boolean; issues: string[] }[] {
  const results: { theme: string; passes: boolean; issues: string[] }[] = [];
  
  (['light', 'dark'] as const).forEach(theme => {
    const issues: string[] = [];
    const themeTokens = tokens[theme];
    
    // Check key contrast ratios
    const botBubbleContrast = checkContrast(themeTokens.headerText, themeTokens.bubbleBot);
    if (botBubbleContrast < 4.5) {
      issues.push(`Bot bubble contrast ratio: ${botBubbleContrast.toFixed(2)} (requires 4.5:1)`);
    }
    
    const userBubbleContrast = checkContrast(themeTokens.chipText, themeTokens.bubbleUser);
    if (userBubbleContrast < 4.5) {
      issues.push(`User bubble contrast ratio: ${userBubbleContrast.toFixed(2)} (requires 4.5:1)`);
    }
    
    results.push({
      theme,
      passes: issues.length === 0,
      issues,
    });
  });
  
  return results;
}

/**
 * Export individual token categories for granular imports
 */
export { tokens as default };
export const lightTheme = tokens.light;
export const darkTheme = tokens.dark;
export const layoutTokens = tokens.layout;
export const typographyTokens = tokens.typography;
export const sizingTokens = tokens.sizing; 