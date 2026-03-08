# LoveSpark Accessibility Framework

Single source of truth for building accessible LoveSpark UIs. Both `/audit-a11y` and `/build-accessible` reference this document.

---

## 1. Core Principles

| Principle | Meaning |
|-----------|---------|
| **Seamless** | Accessibility is built in, not bolted on. Every component ships accessible by default. |
| **Intuitive** | Controls behave as users expect. Standard keyboard patterns, clear affordances, predictable focus. |
| **Easy** | Developers use pre-verified tokens and patterns. No manual contrast math needed. |
| **Warm** | LoveSpark brand warmth extends to accessibility. Friendly language, gentle transitions, no harsh flashing. |

---

## 2. Pre-Verified Color Token Table

All contrast ratios computed against worst-case backgrounds per theme using WCAG 2.1 relative luminance formula. Glass compositing uses `effective = alpha * glass_rgb + (1 - alpha) * bg_rgb` with lightest gradient point.

### Safe Text Combinations (4.5:1+ for normal text)

| Combination | Retro | Dark | Beige | Slate |
|-------------|-------|------|-------|-------|
| `--ls-text-dark` on `--ls-glass` | Use audit tool | Use audit tool | Use audit tool | Use audit tool |
| `--ls-text-dark` on `--ls-bg-pink-light` | Use audit tool | Use audit tool | Use audit tool | Use audit tool |
| `--ls-text-dark` on `--ls-glass-strong` | Use audit tool | Use audit tool | Use audit tool | Use audit tool |
| `--ls-text-muted` on `--ls-glass` | Use audit tool | Use audit tool | Use audit tool | Use audit tool |
| `#fff` on `--ls-btn-hover-bg` | Use audit tool | Use audit tool | Use audit tool | Use audit tool |

> Run `python3 scripts/audit-contrast.py --verbose` for exact ratios. The audit tool is the canonical source for computed contrast values.

### SAFE Token Pairings (verified across all 4 themes)

**For body text:** Always use `--ls-text-dark` on `--ls-glass`, `--ls-bg-gradient`, or `--ls-glass-strong`

**For muted/secondary text:** Use `--ls-text-muted` on `--ls-glass` or `--ls-glass-strong`

**For button text:** Use `#fff` (or `--ls-text-white`) on `--ls-btn-hover-bg` or `--ls-pink-accent`

**For focus indicators:** Use `--ls-focus-ring` (3:1 minimum against adjacent backgrounds)

**For title overrides:**
- Beige: `#3d5a2e` on beige backgrounds
- Slate: `#e8926e` on slate backgrounds

### NEVER Use These Combinations

| Combination | Why |
|-------------|-----|
| `--ls-text-white` for body text on gradient | Fails contrast on retro and beige |
| `--ls-text-muted` on `--ls-bg-gradient` directly | May fail on lighter gradient stops |
| `--ls-glass-border` as text color | Decorative token, not designed for text contrast |
| Hardcoded hex colors for text | Breaks across themes; always use CSS variables |
| `--ls-pink-accent` as text on glass | Not guaranteed 4.5:1 in all themes |

---

## 3. Hard Rules

### NEVER

- Use color as the only state indicator (always pair with text, icon, or pattern change)
- Suppress `outline` without a custom `:focus-visible` replacement
- Create touch targets smaller than 32px x 32px
- Skip `prefers-reduced-motion` media query in any file with animations/transitions
- Use `--ls-text-white` for body text on gradient backgrounds
- Hardcode hex colors for text or backgrounds (use CSS variables)
- Use `setInterval` for DOM watching (use `MutationObserver`)
- Create buttons or links with no visible text or `aria-label`
- Use `tabindex` values greater than 0
- Remove or hide content on `:focus` (breaks keyboard navigation)

### ALWAYS

- Use `--ls-focus-ring` for all focus indicators
- Use `--ls-text-dark` for body text
- Use `--ls-text-muted` for secondary/label text
- Use `--ls-btn-hover-bg` for button hover backgrounds with white text
- Add `role="alertdialog"` with `aria-labelledby` and `aria-describedby` on popup containers
- Add `aria-label` on every interactive element without visible text
- Add `aria-expanded` on buttons that toggle menus/panels
- Add `aria-live="polite"` on regions with dynamic content (counters, status messages)
- Add `alt` text on all images (mascot: `"Sparky -- LoveSpark mascot"`)
- Test keyboard-only navigation before marking any UI complete
- Include `prefers-reduced-motion` block in every CSS file with animations
- Use semantic HTML (`<header>`, `<main>`, `<nav>`, `<section>`, `<footer>`)

---

## 4. Canonical Component Patterns

### 4.1 Popup Shell

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LoveSpark [Name]</title>
  <link rel="stylesheet" href="lib/lovespark-base.css">
  <link rel="stylesheet" href="popup.css">
</head>
<body>
  <div class="popup-container" role="alertdialog"
       aria-labelledby="popup-title" aria-describedby="status-msg">
    <header class="popup-header">
      <div class="header-left">
        <img src="mascot.png" alt="Sparky -- LoveSpark mascot"
             class="mascot" width="36" height="36">
        <span class="header-title" id="popup-title">[Name]</span>
      </div>
      <div class="header-actions">
        <!-- Theme dropdown goes here -->
      </div>
    </header>
    <main class="popup-content">
      <p id="status-msg" aria-live="polite">[Status message]</p>
      <!-- Controls -->
    </main>
    <footer class="popup-footer">
      <!-- Footer content -->
    </footer>
  </div>
</body>
</html>
```

**Requirements:**
- `role="alertdialog"` on container
- `aria-labelledby` pointing to title element
- `aria-describedby` pointing to status/description element
- `lang="en"` on `<html>`
- Mascot with descriptive `alt` text and explicit `width`/`height`

### 4.2 Toggle Switch

```html
<label class="toggle-row">
  <span class="toggle-label">Feature Name</span>
  <span class="toggle-wrap">
    <input type="checkbox" id="feature-toggle" aria-label="Feature Name">
    <span class="toggle-track"><span class="toggle-thumb"></span></span>
  </span>
</label>
```

**CSS requirements:**
- Input hidden with `opacity: 0`, NOT `display: none` (preserves focus)
- `:focus-visible` on track: `outline: 2px solid var(--ls-focus-ring); outline-offset: 2px`
- Checked state: `background: var(--ls-focus-ring)`
- Track min-size: 42x26px (meets 32px touch target with padding)
- `transition: background 0.2s ease` (wrapped in reduced-motion query)

**Keyboard:** Space/Enter toggles. Tab moves to next control.

### 4.3 Tab Group

```html
<nav class="tab-nav" role="tablist" aria-label="Settings categories">
  <button class="tab-btn active" data-tab="one" role="tab"
          id="tab-one" aria-selected="true" aria-controls="panel-one"
          tabindex="0">Tab One</button>
  <button class="tab-btn" data-tab="two" role="tab"
          id="tab-two" aria-selected="false" aria-controls="panel-two"
          tabindex="-1">Tab Two</button>
</nav>

<section class="tab-panel active" data-panel="one" role="tabpanel"
         id="panel-one" aria-labelledby="tab-one">
  <!-- Content -->
</section>
<section class="tab-panel" data-panel="two" role="tabpanel"
         id="panel-two" aria-labelledby="tab-two" hidden>
  <!-- Content -->
</section>
```

**ARIA requirements:**
- `role="tablist"` on nav, `role="tab"` on buttons, `role="tabpanel"` on panels
- `aria-selected="true"` on active tab, `"false"` on others
- `aria-controls` links tab to panel ID
- `aria-labelledby` links panel to tab ID
- Active tab: `tabindex="0"`, inactive tabs: `tabindex="-1"` (roving tabindex)

**Keyboard (roving tabindex):**
- Arrow Left/Right: move between tabs
- Home: first tab
- End: last tab
- Tab: exits tablist to panel content

**CSS:** Active tab `min-height: 32px`, `:focus-visible` outline on all tabs.

### 4.4 Theme Dropdown

```html
<div class="theme-dropdown" id="themeDropdown">
  <button class="theme-dropdown-trigger" id="themeToggle"
          aria-expanded="false" aria-haspopup="true">
    <span id="themeLabel">Retro Pink</span> &blacktriangledown;
  </button>
  <div class="theme-dropdown-menu" id="themeMenu" role="menu">
    <div class="theme-dropdown-header">Change Theme</div>
    <button class="theme-option" data-theme="retro" role="menuitem">Retro Pink</button>
    <button class="theme-option" data-theme="dark" role="menuitem">Dark</button>
    <button class="theme-option" data-theme="beige" role="menuitem">Beige</button>
    <button class="theme-option" data-theme="slate" role="menuitem">Slate</button>
  </div>
</div>
```

**ARIA requirements:**
- `aria-expanded` toggled on open/close
- `aria-haspopup="true"` on trigger
- `role="menu"` on menu container
- `role="menuitem"` on each option

**Keyboard:**
- Enter/Space: open menu
- Arrow Down/Up: navigate options
- Escape: close menu, return focus to trigger
- Home: first option
- End: last option

**CSS:** Menu `z-index: 100`, trigger `:focus-visible` outline. Position `top: calc(100% + 4px)`.

### 4.5 Slider with Value Label

```html
<div class="slider-row">
  <span class="slider-label" id="size-label">Font Size</span>
  <input type="range" id="font-size" min="12" max="32" value="18"
         class="slider" aria-labelledby="size-label"
         aria-valuemin="12" aria-valuemax="32" aria-valuenow="18"
         aria-valuetext="18 pixels">
  <span class="slider-value" id="font-size-val" aria-live="polite">18px</span>
</div>
```

**ARIA requirements:**
- `aria-labelledby` pointing to label
- `aria-valuenow` updated on change
- `aria-valuetext` for human-readable value
- Value display uses `aria-live="polite"`

**Keyboard:** Arrow Left/Right for fine adjustment, Page Up/Down for large steps.

**CSS:** Thumb 20x20px minimum. `:focus-visible` outline on slider track. `outline-offset: 4px`.

### 4.6 Stats Card with Live Region

```html
<div class="stats-card" role="region" aria-label="Statistics">
  <div class="stats-row">
    <span class="stats-label">Today</span>
    <span class="stats-value" id="today-count" aria-live="polite">0</span>
  </div>
  <div class="stats-row">
    <span class="stats-label">All Time</span>
    <span class="stats-value" id="total-count">0</span>
  </div>
</div>
```

**ARIA:** `aria-live="polite"` on dynamically updating values. `role="region"` with `aria-label` on the card.

### 4.7 Primary Button

```html
<button class="btn-pink" aria-label="Save settings">Save</button>
```

**CSS requirements:**
- `min-height: 32px; min-width: 32px` (touch target)
- `padding: 8px 16px`
- Background: `var(--ls-pink-accent)`, hover: `var(--ls-btn-hover-bg)`
- Text: `#fff` (white)
- `:focus-visible`: `outline: 2px solid var(--ls-focus-ring); outline-offset: 2px`
- `:disabled`: reduced opacity, `cursor: not-allowed`

### 4.8 Select Input

```html
<div class="slider-row">
  <span class="slider-label" id="voice-label">Voice</span>
  <select id="tts-voice" class="font-select" aria-labelledby="voice-label">
    <option value="">Default</option>
  </select>
</div>
```

**CSS:** `:focus` border-color uses `var(--ls-focus-ring)`. Min-height for touch target.

---

## 5. Interaction Model

### Focus Management

- **Progressive disclosure:** When a toggle reveals sub-controls, do NOT auto-move focus. Let the user Tab into them naturally.
- **Modal/dropdown open:** Move focus to first focusable element inside.
- **Modal/dropdown close:** Return focus to the trigger element.
- **Tab panels:** When switching tabs, focus moves to the tab, NOT into the panel. User presses Tab to enter panel content.

### Keyboard Shortcuts

| Key | Context | Action |
|-----|---------|--------|
| Tab | Global | Move to next focusable element |
| Shift+Tab | Global | Move to previous focusable element |
| Enter/Space | Button | Activate button |
| Space | Checkbox | Toggle checked state |
| Arrow Left/Right | Tabs (roving tabindex) | Switch between tabs |
| Arrow Down/Up | Menu | Navigate menu items |
| Arrow Left/Right | Slider | Adjust value |
| Escape | Dropdown/menu | Close and return focus to trigger |
| Home | Tabs/menu | First item |
| End | Tabs/menu | Last item |

### Roving Tabindex Pattern (for tabs)

```javascript
const tabs = document.querySelectorAll('[role="tab"]');
tablist.addEventListener('keydown', (e) => {
  const idx = [...tabs].indexOf(e.target);
  let next;
  if (e.key === 'ArrowRight') next = (idx + 1) % tabs.length;
  else if (e.key === 'ArrowLeft') next = (idx - 1 + tabs.length) % tabs.length;
  else if (e.key === 'Home') next = 0;
  else if (e.key === 'End') next = tabs.length - 1;
  else return;
  e.preventDefault();
  tabs[idx].tabIndex = -1;
  tabs[next].tabIndex = 0;
  tabs[next].focus();
  tabs[next].click();
});
```

---

## 6. Typography System

| Element | Min Size | Line Height | Max Width |
|---------|----------|-------------|-----------|
| Body text | 12px | 1.4+ | 65-75ch |
| Labels | 11px | 1.3+ | -- |
| Hints | 10px | 1.3+ | -- |
| Display headings | 9-11px (Press Start 2P is wide) | 1.6+ | -- |
| Long-form content | 14px+ | 1.6+ | 65ch |

**Rules:**
- Never go below 10px for any text
- Use `rem` or `px`, not `em` for font sizes (predictable across nesting)
- Ensure text is resizable up to 200% without loss of content (no `overflow: hidden` on text containers)

---

## 7. Motion System

### Required Pattern

Every CSS file with animations or transitions MUST include:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Acceptable Animations

| Animation | Duration | Usage |
|-----------|----------|-------|
| Color/opacity transitions | 0.15-0.2s | Hover states, theme switching |
| Pop scale animation | 0.35s | Counter updates |
| Slide/fade | 0.2-0.3s | Panel transitions |
| Body background transition | 0.3s | Theme changes |

### Forbidden Animations

- Parallax scrolling
- Infinite loops (spinners OK only with reduced-motion fallback)
- Strobing or rapid flashing (WCAG 2.3.1)
- Auto-playing animations that can't be paused
- Animations longer than 5s without user control

---

## 8. Layout Constraints

| Constraint | Value |
|------------|-------|
| Touch target minimum | 32px x 32px |
| Gap between interactive elements | 8px minimum |
| Popup width | 320-360px |
| Popup max height | ~520-580px |
| Body overflow | `overflow-y: auto` on content area, never clip |
| Z-index: content | auto (default) |
| Z-index: fixed headers | 10 |
| Z-index: dropdowns | 100 |
| Z-index: modals | 200 |

---

## 9. Testing Checklist

### Automated

- [ ] Run `python3 scripts/audit-contrast.py --verbose` -- all checks pass
- [ ] Run `/audit-a11y` -- all categories pass

### Manual: Keyboard

- [ ] Tab through all controls in order
- [ ] Shift+Tab goes backwards correctly
- [ ] Enter/Space activates all buttons
- [ ] Escape closes dropdowns and modals
- [ ] Arrow keys work in tabs and menus
- [ ] Focus is visible on every interactive element
- [ ] Focus returns to trigger when dropdown/modal closes

### Manual: Screen Reader

- [ ] Popup container announced with title and description
- [ ] All toggles announce their label and checked state
- [ ] Tab switching announces selected tab
- [ ] Dynamic counter updates announced via aria-live
- [ ] Images announced with alt text
- [ ] No empty buttons or links

### Manual: Visual (all 4 themes)

- [ ] Retro Pink: text readable on gradient and glass
- [ ] Dark: text readable on dark glass surfaces
- [ ] Beige: title overrides visible, muted text readable
- [ ] Slate: title overrides visible, muted text readable
- [ ] Focus ring visible on all themes
- [ ] Active toggle state distinguishable without color alone

### Manual: Motion

- [ ] Enable "prefers-reduced-motion" in OS/browser
- [ ] Verify all animations are suppressed
- [ ] Verify no layout shift when animations are removed
