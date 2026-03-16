---
name: slidewire-developer
description: Build and refine SlideWire presentations in Laravel/Livewire applications. Use when asked to create, update, or improve slide decks, add slides, configure themes, use fragments, add code blocks or diagrams, or work with the wendelladriel/slidewire package. Triggers on requests like "create a SlideWire presentation", "add slides to...", "build a presentation with SlideWire", "write a slide deck", "add a code slide", "configure SlideWire themes", "add a Mermaid diagram", or "set up vertical navigation".
---

# SlideWire Presentation Builder

SlideWire (`wendelladriel/slidewire`) builds browser-based slide decks using Blade components and Livewire. A `.blade.php` file is compiled to a `PresentationDeck` Livewire component with AlpineJS handling all navigation and transitions.

**Requirements:** PHP ^8.4, Laravel ^12.0, Livewire ^4.2

## Workflow

1. **Scaffold** with `make:slidewire` — generates a Livewire SFC stub
2. **Author** the deck in one Blade file: one `<x-slidewire::deck>` with `<x-slidewire::slide>` children
3. **Register** the route with `Route::slidewire()`
4. **Refine** using themes, transitions, fragments, and content components

```bash
php artisan make:slidewire demo/product-launch --title="Product Launch"
# Interactive mode (no args): prompts for path and title
# --force flag overwrites existing file
```

Presentations are discovered from `config('slidewire.presentation_roots')` (default: `resources/views/pages/slides`). The key `demo/product-launch` maps to `resources/views/pages/slides/demo/product-launch.blade.php`.

## Presentation File Structure

Prefer the Livewire SFC format — it supports PHP logic, public properties, and `with()` data alongside the template:

```blade
<?php
use Livewire\Component;
new class extends Component {
    public string $title = 'My Talk';
    public function with(): array {
        return ['items' => ['Alpha', 'Beta', 'Gamma']];
    }
}; ?>

<x-slidewire::deck theme="aurora" transition="fade" show-progress="true">
    <x-slidewire::slide class="flex flex-col items-center justify-center">
        <h1 class="text-5xl font-bold tracking-tight">{{ $title }}</h1>
        <p class="text-xl text-slate-300 mt-4">Opening slide</p>
    </x-slidewire::slide>

    <x-slidewire::slide>
        <h2 class="text-2xl font-semibold mb-6">Topics</h2>
        @foreach ($items as $item)
            <x-slidewire::fragment>
                <p class="text-lg">{{ $item }}</p>
            </x-slidewire::fragment>
        @endforeach
    </x-slidewire::slide>
</x-slidewire::deck>
```

Plain Blade (no PHP logic) also works — just the `<x-slidewire::deck>` tree.

## Route Registration

```php
use Illuminate\Support\Facades\Route;

Route::slidewire('/slides/product-launch', 'demo/product-launch');
// Named: slidewire.demo.product-launch
// Returns 404 if the presentation key cannot be resolved
```

## Settings Precedence

```
slide attribute → deck attribute → config('slidewire.slides')
```

Set shared behavior on the deck, override intentionally per-slide.

## Core Components

### `<x-slidewire::deck>` — Presentation Wrapper

```blade
<x-slidewire::deck
    theme="aurora"
    transition="fade"
    transition-speed="default"
    transition-duration="350"
    auto-slide="0"
    auto-slide-pause-on-interaction="true"
    show-controls="true"
    show-progress="true"
    show-fullscreen-button="true"
    highlight-theme="catppuccin-mocha"
>
```

### `<x-slidewire::slide>` — Single Slide

```blade
<x-slidewire::slide
    class="bg-slate-900 text-white"
    theme="black"
    transition="zoom"
    auto-animate="true"
    auto-animate-duration="500"
    background-image="https://example.com/bg.jpg"
    background-opacity="0.35"
    background-size="cover"
    background-position="center"
>
    <h2>Slide content</h2>
</x-slidewire::slide>
```

See **references/components.md** for all attribute tables.

### `<x-slidewire::vertical-slide>` — Vertical Stack

Groups slides into one horizontal column with vertical navigation:

```blade
<x-slidewire::vertical-slide>
    <x-slidewire::slide><h2>Overview</h2></x-slidewire::slide>
    <x-slidewire::slide><h2>Detail A</h2></x-slidewire::slide>
    <x-slidewire::slide><h2>Detail B</h2></x-slidewire::slide>
</x-slidewire::vertical-slide>
```

Up/down arrows appear in controls only when vertical slides exist.

### `<x-slidewire::fragment>` — Progressive Reveal

Reveals content incrementally. When unrevealed fragments exist, `Next` reveals the next fragment instead of advancing to the next slide.

```blade
<x-slidewire::slide>
    <h2>Rollout</h2>
    <x-slidewire::fragment :index="0"><p>Private beta</p></x-slidewire::fragment>
    <x-slidewire::fragment :index="1"><p>Pilot accounts</p></x-slidewire::fragment>
    <x-slidewire::fragment :index="2"><p>General availability</p></x-slidewire::fragment>
</x-slidewire::slide>
```

Omit `:index` to auto-count fragments within the slide.

### `<x-slidewire::code>` — Highlighted Code Block

```blade
<x-slidewire::code language="php" size="text-lg" theme="catppuccin-latte" font="JetBrainsMono">
function greet(string $name): string {
    return "Hello, {$name}!";
}
</x-slidewire::code>
```

Theme resolution: explicit `theme` attr → active deck theme's `highlightTheme` → config default.

### `<x-slidewire::markdown>` — Markdown Renderer

```blade
<x-slidewire::markdown size="text-base">
## Key Metrics

- **Activation rate:** 62%
- **Churn:** 1.8%

```php
echo 'fenced code blocks are highlighted';
```
</x-slidewire::markdown>
```

Use `markdown` for narrative and mixed prose/code. Fenced code blocks are protected from Blade compilation automatically.

### `<x-slidewire::diagram>` — Mermaid Diagram

```blade
<x-slidewire::diagram theme="dark">
flowchart LR
    A[Request] --> B{Auth?}
    B -- Yes --> C[Handler]
    B -- No --> D[401]
</x-slidewire::diagram>
```

Mermaid is lazy-loaded from CDN (mermaid@11). Theme: `dark` or `default`.

## Transition Reference

| Name | Description |
|------|-------------|
| `slide` | Horizontal/vertical slide (default) |
| `fade` | Opacity crossfade |
| `zoom` | Scale + opacity |
| `convex` | Same as slide |
| `concave` | Same as slide |
| `none` | Instant cut |

Speeds: `fast` (55% of base), `default`, `slow` (175% of base)

## Auto-Animate

Smoothly transitions matching elements between consecutive slides using FLIP animation. Add `auto-animate="true"` to both slides and tag elements with matching `data-auto-animate-id`:

```blade
<x-slidewire::slide auto-animate="true">
    <div data-auto-animate-id="card" class="p-4 bg-slate-800 rounded w-1/3">
        <h3>Before</h3>
    </div>
</x-slidewire::slide>

<x-slidewire::slide auto-animate="true" auto-animate-duration="600">
    <div data-auto-animate-id="card" class="p-4 bg-slate-800 rounded w-full">
        <h3>After</h3>
    </div>
</x-slidewire::slide>
```

Elements without a matching source animate in from `translateY(12px)` + fade. The regular slide transition is suppressed when auto-animate is active.

## Navigation

- **Keyboard:** Arrow keys, Space bar (linear advance)
- **Click/tap:** Click stage to advance; click controls to navigate
- **Touch:** Swipe left/right/up/down (scroll-aware)
- **Deep link:** `#/slide/H` for horizontal (1-indexed), `#/slide/H/V` for vertical

## Built-in Themes

| Name | Background | Highlight |
|------|-----------|-----------|
| `default` | Blue-slate gradient | Catppuccin Mocha |
| `black` | `bg-slate-900` | Catppuccin Mocha |
| `white` | `bg-white` | Catppuccin Latte |
| `aurora` | Emerald-cyan-slate gradient | Catppuccin Mocha |
| `sunset` | Rose-orange-amber gradient | Catppuccin Mocha |
| `neon` | Fuchsia-violet-cyan gradient | Catppuccin Mocha |
| `solarized` | `bg-yellow-50` | Catppuccin Latte |

For custom themes and font configuration, see **references/theming.md**.
For config file structure and DTOs, see **references/configuration.md**.
For full component attribute tables, see **references/components.md**.

## Common Patterns

**Title slide:**
```blade
<x-slidewire::slide class="flex flex-col items-center justify-center text-center">
    <h1 class="text-6xl font-bold tracking-tight">Talk Title</h1>
    <p class="text-2xl text-slate-400 mt-6">Speaker · Event · Date</p>
</x-slidewire::slide>
```

**Section divider:**
```blade
<x-slidewire::slide class="bg-gradient-to-br from-emerald-900 to-slate-950 flex items-center justify-center">
    <h2 class="text-5xl font-semibold text-emerald-300">Part 2</h2>
</x-slidewire::slide>
```

**Image background:**
```blade
<x-slidewire::slide
    background-image="https://example.com/photo.jpg"
    background-size="cover"
    background-position="center"
    background-opacity="0.4"
    class="flex items-end p-12"
>
    <h2 class="text-4xl font-bold text-white drop-shadow">Caption text</h2>
</x-slidewire::slide>
```

## Reference Files

- **references/components.md** — Full attribute tables for all components
- **references/configuration.md** — Config file structure, SlidesConfig, ThemeConfig, FontConfig DTOs
- **references/theming.md** — Built-in theme details, custom themes, Phiki highlight themes, fonts
