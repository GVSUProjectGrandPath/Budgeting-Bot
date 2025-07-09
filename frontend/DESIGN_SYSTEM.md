# PGPBOT Frontend Design System 2.0

## Overview

The frontend has been completely revamped with a modern design token architecture that supports:

- ✅ **Theme Support**: Light/dark mode with system preference detection
- ✅ **Accessibility**: WCAG-AA contrast ratios and proper focus management
- ✅ **Responsive Design**: Mobile-first approach with fluid layouts
- ✅ **Brand Consistency**: Exportable token map for unified branding
- ✅ **Performance**: Smooth animations and optimized rendering
- ✅ **Backend Health**: Latency-based header hue shift indicator

## Key Features

### 1. Design Token Architecture

All colors, spacing, typography, and sizing are centralized in CSS custom properties:

```css
:root {
  --surface-0: #FDF6E5;
  --bubble-bot: #44B59D;
  --chip-bg: #7E66C1;
  /* ... and many more */
}
```

### 2. Theme System

- **Auto-detection**: Respects `prefers-color-scheme`
- **Manual override**: Theme toggle button in header
- **Persistence**: Saves preference to localStorage
- **Smooth transitions**: 120ms ease transitions between themes

### 3. Layout Structure

- **Fluid container**: Max-width 960px with responsive breakpoints
- **66/34 split**: Chat takes 66% width, sidebar 34%
- **Sticky positioning**: Header and sidebar remain visible during scroll
- **24px gap**: Consistent spacing between columns

### 4. Typography

- **Font**: Inter (400, 600, 700 weights)
- **Header**: 20px, 700 weight
- **Body**: 16px, 400 weight, 1.5 line-height
- **Quick chips**: 14px, 600 weight, uppercase

### 5. Component Specifications

- **Header height**: 64px
- **Chat bubbles**: Max 70% width, 24px border-radius
- **Quick chips**: 44px height, 12px border-radius
- **Composer**: 72px height with proper input padding
- **Icons**: 24px square, 1.5px stroke-width

## Theme Token Export (Angle A)

The design system can be imported by marketing sites for brand consistency:

```typescript
import { tokens, applyTokens, getTokensCSS } from './tokens';

// Apply theme programmatically
applyTokens('dark');

// Get CSS string for embedding
const css = getTokensCSS('light');

// Access individual token categories
import { lightTheme, darkTheme, layoutTokens } from './tokens';
```

## Backend Health Indicator (Angle B)

The header background shifts hue based on API response times:

- **Green (default)**: Fast responses (< 200ms)
- **Yellow**: Moderate latency (200-500ms)  
- **Red**: High latency (> 500ms)

The hue shift is calculated as: `hsl(${latency > 500 ? 0 : 51 - hueShift}, 100%, 50%)`

## Accessibility Features

### WCAG-AA Compliance
- ✅ Bot bubble contrast: 4.5:1 ratio minimum
- ✅ User bubble contrast: 4.5:1 ratio minimum
- ✅ Focus indicators: 2px outline with offset
- ✅ High contrast mode support

### Keyboard Navigation
- ✅ Tab order follows logical flow
- ✅ Skip links and proper headings
- ✅ Form labels and ARIA attributes
- ✅ Screen reader announcements

### Motion Preferences
- ✅ Respects `prefers-reduced-motion`
- ✅ Disables animations when requested
- ✅ Maintains functionality without motion

## Responsive Breakpoints

```css
@media (max-width: 768px) {
  /* Mobile layout: 
     - Stacked columns
     - Increased bubble max-width
     - Adjusted padding */
}
```

## Component Classes

### Layout
- `.app` - Root application container
- `.main-container` - Central content area (max-width: 960px)
- `.chat-column` - Chat area (66% width)
- `.sidebar-column` - Information panel (34% width)

### Interactive Elements
- `.bubble.user` - User message bubble
- `.bubble.bot` - Bot message bubble  
- `.quick-chip` - Quick action buttons
- `.theme-toggle` - Theme switcher button

### Form Elements
- `.input-field` - Text input styling
- `.send-button` - Message send button
- `.composer` - Input area container

## Performance Considerations

- **CSS Custom Properties**: Fast theme switching without DOM manipulation
- **Smooth Animations**: Maximum 0.45s duration, optimized timing functions
- **Efficient Selectors**: Minimal nesting, class-based targeting
- **Font Loading**: Inter font with display=swap optimization

## Browser Support

- ✅ Modern browsers (Chrome 88+, Firefox 85+, Safari 14+)
- ✅ CSS Custom Properties required
- ✅ CSS Grid and Flexbox support required
- ✅ Graceful degradation for older browsers

## Development

To run the development server:

```bash
cd frontend
npm start
```

The design system is fully contained in:
- `src/App.css` - Complete design system styles
- `src/tokens.ts` - Exportable token definitions
- `src/App.tsx` - Component implementation

## Future Enhancements

1. **Color scheme picker**: Beyond light/dark themes
2. **Font size controls**: User-adjustable typography scale
3. **Motion controls**: Granular animation preferences
4. **Density options**: Compact/comfortable/spacious modes 