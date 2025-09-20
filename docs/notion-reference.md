# Notion CSS Styles Reference

Based on investigation of Notion's styling system, here are the basic CSS rules used by Notion for markdown pages:

## Typography & Fonts

### Font Families
```css
/* Default Notion font stacks */
--theme--font_sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, 'Apple Color Emoji', Arial, sans-serif, 'Segoe UI Emoji', 'Segoe UI Symbol';
--theme--font_serif: Lyon-Text, Georgia, YuMincho, 'Yu Mincho', 'Hiragino Mincho ProN', 'Hiragino Mincho Pro', 'Songti TC', 'Songti SC', SimSun, 'Nanum Myeongjo', NanumMyeongjo, Batang, serif;
--theme--font_mono: iawriter-mono, Nitti, Menlo, Courier, monospace;
--theme--font_code: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, Courier, monospace;
```

### Font Sizes
```css
.notion-text-block {
    font-size: 16px; /* Default body text */
    margin-top: 3px;
    margin-bottom: 1px;
}

/* When small text is enabled */
.notion-text-block[small-text] {
    font-size: 14px;
}

/* Lists and other content blocks */
.notion-bulleted_list-block,
.notion-numbered_list-block,
.notion-toggle-block,
.notion-to_do-list,
.notion-callout-block,
.notion-equation-block,
.notion-page-block {
    font-size: 16px;
}

/* Code blocks */
.notion-code-block {
    font-size: 14px;
}

/* Quote blocks */
.notion-quote-block {
    font-size: 16px;
}
```

## Headings

### Font Sizes and Spacing
```css
/* Heading 1 */
h1, .notion-header-block {
    font-size: 40px;
    font-weight: 700;
    line-height: 1.2;
    margin-top: 2em;
    margin-bottom: 4px;
}

/* Heading 2 */
h2, .notion-sub_header-block {
    font-size: 30px;
    font-weight: 600;
    line-height: 1.3;
    margin-top: 1.4em;
    margin-bottom: 1px;
}

/* Heading 3 */
h3, .notion-sub_sub_header-block {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.3;
    margin-top: 1em;
    margin-bottom: 1px;
}
```

## Text Blocks and Paragraphs

### Basic Text Styling
```css
.notion-text-block {
    margin-top: 3px;
    margin-bottom: 1px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Inline text styling */
strong, .notion-bold {
    font-weight: 600;
}

em, .notion-italic {
    font-style: italic;
}

.notion-strikethrough {
    text-decoration: line-through;
}

.notion-underline {
    text-decoration: underline;
}

/* Inline code */
.notion-inline-code {
    font-family: var(--theme--font_code);
    background: rgba(135, 131, 120, 0.15);
    border-radius: 3px;
    padding: 0.2em 0.4em;
    font-size: 85%;
}
```

## Lists

### Bulleted Lists
```css
.notion-bulleted_list-block {
    margin-top: 1px;
    margin-bottom: 1px;
    margin-left: 1.5em;
    list-style-type: disc;
}

.notion-bulleted_list-block .notion-list-item {
    padding-left: 0.1em;
    line-height: 1.5;
}
```

### Numbered Lists
```css
.notion-numbered_list-block {
    margin-top: 1px;
    margin-bottom: 1px;
    margin-left: 1.5em;
    list-style-type: decimal;
}

.notion-numbered_list-block .notion-list-item {
    padding-left: 0.1em;
    line-height: 1.5;
}
```

### To-Do Lists
```css
.notion-to_do-block {
    display: flex;
    align-items: flex-start;
    margin-top: 1px;
    margin-bottom: 1px;
}

.notion-to_do-block .notion-checkbox {
    margin-right: 8px;
    margin-top: 3px;
    width: 16px;
    height: 16px;
    border-radius: 3px;
    border: 1.5px solid rgba(55, 53, 47, 0.35);
}
```

## Code Blocks

### Code Block Styling
```css
.notion-code-block {
    font-family: var(--theme--font_code);
    background: rgb(247, 246, 243);
    border-radius: 3px;
    padding: 16px;
    margin-top: 4px;
    margin-bottom: 4px;
    font-size: 14px;
    line-height: 1.4;
    white-space: pre;
    overflow-x: auto;
}

/* Dark mode code blocks */
.dark .notion-code-block {
    background: rgb(47, 52, 55);
    color: rgb(203, 204, 205);
}
```

## Quote Blocks

### Quote Styling
```css
.notion-quote-block {
    border-left: 3px solid currentcolor;
    padding-left: 14px;
    padding-right: 14px;
    padding-top: 4px;
    padding-bottom: 4px;
    margin-top: 4px;
    margin-bottom: 4px;
    font-size: 16px;
    line-height: 1.7;
    color: rgb(120, 119, 116);
}
```

## Callout Blocks

### Callout Styling
```css
.notion-callout-block {
    display: flex;
    border-radius: 3px;
    padding: 16px;
    margin-top: 4px;
    margin-bottom: 4px;
    background: rgb(241, 241, 239);
}

.notion-callout-block .notion-record-icon {
    margin-right: 8px;
    margin-top: 1px;
    flex-shrink: 0;
}

/* Colored callouts */
.notion-callout-block[data-color="gray"] {
    background: rgb(241, 241, 239);
}

.notion-callout-block[data-color="brown"] {
    background: rgb(244, 238, 238);
}

.notion-callout-block[data-color="orange"] {
    background: rgb(251, 236, 221);
}

.notion-callout-block[data-color="yellow"] {
    background: rgb(251, 243, 219);
}

.notion-callout-block[data-color="green"] {
    background: rgb(237, 243, 236);
}

.notion-callout-block[data-color="blue"] {
    background: rgb(231, 243, 248);
}

.notion-callout-block[data-color="purple"] {
    background: rgb(244, 240, 247);
}

.notion-callout-block[data-color="pink"] {
    background: rgb(249, 238, 243);
}

.notion-callout-block[data-color="red"] {
    background: rgb(253, 235, 236);
}
```

## Tables

### Table Styling
```css
.notion-table {
    border-collapse: collapse;
    border-spacing: 0;
    width: 100%;
    margin-top: 6px;
    margin-bottom: 6px;
}

.notion-table-cell {
    border: 1px solid rgb(233, 233, 231);
    padding: 8px 9px;
    min-height: 33px;
    font-size: 14px;
    line-height: 1.4;
    vertical-align: top;
}

.notion-table-header-cell {
    background: rgb(247, 246, 243);
    font-weight: 500;
}
```

## Images

### Image Styling
```css
.notion-image-block {
    margin-top: 4px;
    margin-bottom: 4px;
    border-radius: 0;
}

.notion-image-block img {
    max-width: 100%;
    height: auto;
    border-radius: 0;
}

/* Custom image borders (when applied) */
.notion-image-block.custom-border {
    border: 10px solid #eee;
    border-radius: 10px;
}
```

## Dividers

### Divider Styling
```css
.notion-divider {
    border: none;
    border-top: 1px solid rgba(55, 53, 47, 0.16);
    margin: 16px 0;
    height: 1px;
}
```

## Page Layout

### Page Container
```css
.notion-page-content {
    max-width: 708px; /* Default width */
    margin: 0 auto;
    padding: 0 96px;
    font-family: var(--theme--font_sans);
}

/* Full width mode */
.notion-page-content.full-width {
    max-width: none;
    padding: 0 96px;
}

/* Small text mode */
.notion-page-content.small-text {
    font-size: 14px;
}

.notion-page-content.small-text .notion-text-block {
    font-size: 14px;
}
```

### Page Margins and Padding
```css
/* Default page margins */
.notion-page {
    padding-top: 30px;
    padding-bottom: 30px;
}

/* Block spacing */
.notion-block {
    margin-top: 1px;
    margin-bottom: 1px;
}

/* Larger spacing for certain blocks */
.notion-header-block,
.notion-sub_header-block,
.notion-sub_sub_header-block {
    margin-top: 1.4em;
    margin-bottom: 0.1em;
}
```

## Colors and Themes

### Color Variables
```css
:root {
    /* Light theme colors */
    --theme--fg-default: rgb(55, 53, 47);
    --theme--fg-muted: rgb(120, 119, 116);
    --theme--bg-default: rgb(255, 255, 255);
    --theme--bg-secondary: rgb(247, 246, 243);
    --theme--border-default: rgba(55, 53, 47, 0.16);
}

/* Dark theme colors */
.dark {
    --theme--fg-default: rgb(255, 255, 255);
    --theme--fg-muted: rgba(255, 255, 255, 0.71);
    --theme--bg-default: rgb(25, 25, 25);
    --theme--bg-secondary: rgb(47, 52, 55);
    --theme--border-default: rgba(255, 255, 255, 0.13);
}
```

### Text Colors
```css
/* Available text colors */
.notion-gray { color: rgb(120, 119, 116); }
.notion-brown { color: rgb(159, 107, 83); }
.notion-orange { color: rgb(217, 115, 13); }
.notion-yellow { color: rgb(203, 145, 47); }
.notion-green { color: rgb(68, 131, 97); }
.notion-blue { color: rgb(51, 126, 169); }
.notion-purple { color: rgb(144, 101, 176); }
.notion-pink { color: rgb(193, 76, 138); }
.notion-red { color: rgb(212, 76, 71); }

/* Background colors */
.notion-gray_background { background: rgb(241, 241, 239); }
.notion-brown_background { background: rgb(244, 238, 238); }
.notion-orange_background { background: rgb(251, 236, 221); }
.notion-yellow_background { background: rgb(251, 243, 219); }
.notion-green_background { background: rgb(237, 243, 236); }
.notion-blue_background { background: rgb(231, 243, 248); }
.notion-purple_background { background: rgb(244, 240, 247); }
.notion-pink_background { background: rgb(249, 238, 243); }
.notion-red_background { background: rgb(253, 235, 236); }
```

## Line Heights and Spacing

### General Line Heights
```css
/* Standard line heights across elements */
.notion-text-block { line-height: 1.5; }
.notion-header-block { line-height: 1.2; }
.notion-sub_header-block { line-height: 1.3; }
.notion-sub_sub_header-block { line-height: 1.3; }
.notion-quote-block { line-height: 1.7; }
.notion-code-block { line-height: 1.4; }
.notion-list-item { line-height: 1.5; }
```

## Responsive Design

### Mobile Breakpoints
```css
@media (max-width: 768px) {
    .notion-page-content {
        padding: 0 20px;
        max-width: 100%;
    }
    
    .notion-header-block {
        font-size: 32px;
    }
    
    .notion-sub_header-block {
        font-size: 24px;
    }
    
    .notion-sub_sub_header-block {
        font-size: 20px;
    }
}
```
