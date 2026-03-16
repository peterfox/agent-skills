# SlideWire Configuration Reference

Publish the config file:

```bash
php artisan vendor:publish --tag=slidewire-config
# Writes: config/slidewire.php
```

## Config Structure

```php
use Phiki\Theme\Theme;
use WendellAdriel\SlideWire\DTOs\FontConfig;
use WendellAdriel\SlideWire\DTOs\HighlightConfig;
use WendellAdriel\SlideWire\DTOs\SlidesConfig;
use WendellAdriel\SlideWire\DTOs\ThemeConfig;
use WendellAdriel\SlideWire\DTOs\ThemeFont;
use WendellAdriel\SlideWire\Enums\FontSource;
use WendellAdriel\SlideWire\Enums\SlideTransition;
use WendellAdriel\SlideWire\Enums\SlideTransitionSpeed;

return [
    'presentation_roots' => [
        resource_path('views/pages/slides'),
    ],

    'slides' => new SlidesConfig(...),

    'themes' => [
        'my-theme' => new ThemeConfig(...),
        // Built-in themes are always available regardless of this array.
    ],

    'fonts' => [
        'Inter' => new FontConfig(source: FontSource::Google, weights: [400, 600, 700]),
        'JetBrainsMono' => new FontConfig(source: FontSource::Google, weights: [400, 700]),
    ],
];
```

---

## `SlidesConfig`

Global defaults for all presentations. Overridden by deck and slide attributes.

```php
new SlidesConfig(
    theme: 'default',                             // built-in or custom theme name
    showControls: true,                           // navigation arrows
    showProgress: true,                           // progress bar
    showFullscreenButton: true,                   // fullscreen toggle
    keyboard: true,                               // metadata only — nav always on
    touch: true,                                  // metadata only — swipe always on
    transition: SlideTransition::Slide,           // Slide|Fade|Zoom|Convex|Concave|None
    transitionDuration: 350,                      // base ms
    transitionSpeed: SlideTransitionSpeed::Default, // Default|Fast|Slow
    autoSlide: 0,                                 // ms, 0 = disabled
    autoSlidePauseOnInteraction: true,
    highlight: new HighlightConfig(
        enabled: true,
        theme: Theme::CatppuccinMocha,            // Phiki\Theme\Theme enum
        font: 'JetBrainsMono',
        fontSize: 'text-base',                    // Tailwind text-size class
    ),
)
```

`SlideTransition` enum values: `Slide`, `Fade`, `Zoom`, `Convex`, `Concave`, `None`
`SlideTransitionSpeed` enum values: `Default`, `Fast`, `Slow`

---

## `ThemeConfig`

Defines a named theme. Reference by its key in `config('slidewire.themes')`.

```php
new ThemeConfig(
    background: 'bg-gradient-to-br from-slate-900 via-blue-950 to-slate-950',
    highlightTheme: Theme::CatppuccinMocha,
    title: new ThemeFont(
        font: 'Inter',
        color: 'text-slate-50',
        size: 'text-4xl',
    ),
    text: new ThemeFont(
        font: 'Inter',
        color: 'text-slate-200',
        size: 'text-lg',
    ),
)
```

`background` is a Tailwind class string applied to the slide container. Use Tailwind bg utilities for solid colors, gradients, or any background-color approach.

To register a custom theme:

```php
// config/slidewire.php
'themes' => [
    'brand' => new ThemeConfig(
        background: 'bg-gradient-to-br from-indigo-950 to-purple-900',
        highlightTheme: Theme::CatppuccinMocha,
        title: new ThemeFont(font: 'Inter', color: 'text-indigo-100', size: 'text-5xl'),
        text: new ThemeFont(font: 'Inter', color: 'text-indigo-200', size: 'text-xl'),
    ),
],
```

Then use it: `<x-slidewire::deck theme="brand">`.

---

## `ThemeFont`

Defines typography for a theme role (title or body text).

```php
new ThemeFont(
    font: 'Inter',         // font name — must exist in config('slidewire.fonts')
    color: 'text-slate-50', // Tailwind text-color class
    size: 'text-4xl',      // Tailwind text-size class
)
```

---

## `HighlightConfig`

Controls syntax highlighting defaults.

```php
new HighlightConfig(
    enabled: true,
    theme: Theme::CatppuccinMocha, // Phiki\Theme\Theme enum case
    font: 'JetBrainsMono',
    fontSize: 'text-base',
)
```

---

## `FontConfig`

Registers a font for use in themes and code blocks.

```php
new FontConfig(
    source: FontSource::Google,  // Google|System
    weights: [400, 600, 700],    // Only used for Google fonts
)
```

`FontSource::Google` — injects a Google Fonts `<link>` tag automatically.
`FontSource::System` — uses the system font stack, no loading required.

Adding a custom Google font:

```php
// config/slidewire.php
'fonts' => [
    'Inter' => new FontConfig(source: FontSource::Google, weights: [400, 600, 700]),
    'JetBrainsMono' => new FontConfig(source: FontSource::Google, weights: [400, 700]),
    'Poppins' => new FontConfig(source: FontSource::Google, weights: [400, 700, 900]),
],
```

---

## `presentation_roots`

Array of absolute directory paths where presentation files live. `make:slidewire` writes to the first root. Keys are derived from the path relative to any root.

```php
'presentation_roots' => [
    resource_path('views/pages/slides'),      // default
    resource_path('views/presentations'),     // additional root
],
```

Path normalization: leading/trailing slashes trimmed, backslashes converted, `..` segments stripped.
