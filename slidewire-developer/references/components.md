# SlideWire Component Attribute Reference

## `<x-slidewire::deck>`

Renders as `<section class="slidewire-deck" data-*>`. All attributes are optional strings.

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `theme` | string | `'default'` | Built-in or custom theme name |
| `transition` | string | `'slide'` | slide / fade / zoom / convex / concave / none |
| `transition-speed` | string | `'default'` | fast / default / slow |
| `transition-duration` | string | `'350'` | Base duration in ms |
| `auto-slide` | string | `'0'` | Auto-advance interval in ms (0 = disabled) |
| `auto-slide-pause-on-interaction` | string | `'true'` | Pause auto-slide when user interacts |
| `show-controls` | string | `'true'` | Show navigation arrow controls |
| `show-progress` | string | `'true'` | Show progress bar |
| `show-fullscreen-button` | string | `'true'` | Show fullscreen toggle button |
| `keyboard` | string | `'true'` | Keyboard nav metadata (navigation always enabled) |
| `touch` | string | `'true'` | Touch/swipe metadata (swipe always enabled) |
| `highlight-theme` | string | theme default | Phiki theme name for code highlighting |

---

## `<x-slidewire::slide>`

Renders as `<article class="slidewire-slide slidewire-transition-{transition}" data-*>`.

### Visual

| Attribute | Description |
|-----------|-------------|
| `class` | Tailwind classes for background, text color, layout |
| `theme` | Override the active theme for this slide |

### Transitions

| Attribute | Description |
|-----------|-------------|
| `transition` | Per-slide transition override |
| `transition-speed` | Per-slide speed override |
| `auto-slide` | Per-slide auto-advance interval in ms |

### Backgrounds

| Attribute | Description |
|-----------|-------------|
| `background-image` | URL of background image |
| `background-video` | URL of background video |
| `background-video-loop` | `"true"` / `"false"` |
| `background-video-muted` | `"true"` / `"false"` |
| `background-size` | CSS background-size (e.g. `cover`) |
| `background-position` | CSS background-position (e.g. `center`) |
| `background-repeat` | CSS background-repeat |
| `background-opacity` | Float 0–1 as string — dims the background layer |
| `background-transition` | Transition name for background change |

### Auto-Animate

| Attribute | Description |
|-----------|-------------|
| `auto-animate` | `"true"` — enables FLIP animation between this and the next slide |
| `auto-animate-duration` | Duration in ms as string |
| `auto-animate-easing` | CSS easing function |

Tag elements on both sides of the transition with `data-auto-animate-id="same-id"`.

---

## `<x-slidewire::vertical-slide>`

Renders as `<section class="slidewire-vertical-slide slidewire-stack">`. Contains `<x-slidewire::slide>` children only.

No configurable attributes — styling and transitions are inherited from child slides.

---

## `<x-slidewire::fragment>`

Renders as `<span class="slidewire-fragment" data-fragment data-fragment-index="N">`.

| Attribute | Description |
|-----------|-------------|
| `:index` | Integer — explicit fragment reveal order (0-based). Omit to auto-count. |

Multiple fragments on one slide reveal in index order. After all fragments are visible, the next navigation call advances to the next slide.

---

## `<x-slidewire::code>`

Renders a syntax-highlighted code block using Phiki.

| Attribute | Description |
|-----------|-------------|
| `language` | Language identifier (e.g. `php`, `js`, `bash`, `json`) |
| `theme` | Phiki theme name override (see theming.md) |
| `font` | Font name override |
| `size` | Tailwind text-size class (e.g. `text-sm`, `text-base`, `text-lg`) |

Theme resolution order: `theme` attr → active deck theme's `highlightTheme` → `config('slidewire.slides.highlight.theme')`.

Falls back to unstyled `<pre>` block if Phiki is unavailable.

---

## `<x-slidewire::markdown>`

Renders Markdown to HTML with fenced code block highlighting.

| Attribute | Description |
|-----------|-------------|
| `size` | Tailwind text-size class applied to code blocks |

Fenced code blocks inside the slot are base64-encoded before Blade processes the template, preventing Blade from treating `{{ }}` or `@` directives inside code samples as Blade syntax.

---

## `<x-slidewire::diagram>`

Renders a Mermaid diagram. Mermaid is lazy-loaded from CDN (`mermaid@11`) and re-renders after Livewire morphs.

| Attribute | Description |
|-----------|-------------|
| `theme` | Mermaid theme: `dark` or `default` |

Slot content is the raw Mermaid source (flowchart, sequenceDiagram, classDiagram, etc.).
