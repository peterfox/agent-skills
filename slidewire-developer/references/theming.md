# SlideWire Theming Reference

## Built-in Themes

| Name | Background Classes | Highlight Theme |
|------|--------------------|----------------|
| `default` | `bg-gradient-to-br from-slate-900 via-blue-950 to-slate-950 text-slate-50` | Catppuccin Mocha |
| `black` | `bg-slate-900 text-slate-200` | Catppuccin Mocha |
| `white` | `bg-white text-zinc-800` | Catppuccin Latte |
| `aurora` | `bg-gradient-to-br from-emerald-950 via-cyan-900 to-slate-950 text-emerald-50` | Catppuccin Mocha |
| `sunset` | `bg-gradient-to-br from-rose-950 via-orange-900 to-amber-700 text-orange-50` | Catppuccin Mocha |
| `neon` | `bg-gradient-to-br from-fuchsia-950 via-violet-900 to-cyan-900 text-fuchsia-50` | Catppuccin Mocha |
| `solarized` | `bg-yellow-50 text-slate-600` | Catppuccin Latte |

Built-in themes are always available — they do not need to be declared in config.

---

## Defining Custom Themes

Add to `config/slidewire.php` under the `themes` key:

```php
use Phiki\Theme\Theme;
use WendellAdriel\SlideWire\DTOs\ThemeConfig;
use WendellAdriel\SlideWire\DTOs\ThemeFont;

'themes' => [
    'brand' => new ThemeConfig(
        background: 'bg-gradient-to-br from-indigo-950 to-purple-900',
        highlightTheme: Theme::CatppuccinMocha,
        title: new ThemeFont(font: 'Inter', color: 'text-indigo-100', size: 'text-5xl'),
        text: new ThemeFont(font: 'Inter', color: 'text-indigo-200', size: 'text-xl'),
    ),
],
```

Then reference it: `<x-slidewire::deck theme="brand">`.

The `background` field is a raw Tailwind class string applied to the slide container. You can use:
- `bg-{color}-{shade}` for solids
- `bg-gradient-to-{dir} from-* via-* to-*` for gradients
- Append `text-*` for default text color

---

## ThemeFont Fields

| Field | Description |
|-------|-------------|
| `font` | Font family name — must exist in `config('slidewire.fonts')` |
| `color` | Tailwind text-color class (e.g. `text-slate-50`) |
| `size` | Tailwind text-size class (e.g. `text-4xl`) |

The `title` font styles `h1`/`h2` elements; `text` styles body content.

---

## Font Configuration

Two built-in fonts ship with SlideWire: **Inter** (UI text) and **JetBrainsMono** (code). Both are loaded from Google Fonts automatically.

Adding a custom Google font:

```php
use WendellAdriel\SlideWire\DTOs\FontConfig;
use WendellAdriel\SlideWire\Enums\FontSource;

'fonts' => [
    'Inter' => new FontConfig(source: FontSource::Google, weights: [400, 600, 700]),
    'JetBrainsMono' => new FontConfig(source: FontSource::Google, weights: [400, 700]),
    'Poppins' => new FontConfig(source: FontSource::Google, weights: [400, 700, 900]),
    'Fira Code' => new FontConfig(source: FontSource::Google, weights: [400, 500]),
],
```

Using a system font (no external load):

```php
'Menlo' => new FontConfig(source: FontSource::System),
```

`FontSource` enum values: `Google`, `System`

Font weights are only used for Google Fonts (`<link rel="stylesheet">` query string). System fonts ignore weights.

---

## Code Highlight Themes (Phiki)

Phiki (`phiki/phiki`) provides syntax highlighting. Use `Theme::*` enum cases from `Phiki\Theme\Theme`.

Common choices:

| `Theme::*` | Style |
|-----------|-------|
| `CatppuccinMocha` | Dark pastel (default for dark themes) |
| `CatppuccinLatte` | Light pastel (default for light themes) |
| `CatppuccinFrappe` | Mid-tone purple-grey |
| `CatppuccinMacchiato` | Dark with warm tones |
| `GithubDark` | GitHub dark mode |
| `GithubLight` | GitHub light mode |
| `DraculaSoft` | Soft Dracula palette |
| `Dracula` | Classic Dracula |
| `NordDeep` | Nord deep variant |
| `OneDarkPro` | VS Code One Dark |
| `SolarizedLight` | Solarized light |
| `SolarizedDark` | Solarized dark |
| `Vesper` | Dark minimal |
| `TokyoNight` | Tokyo Night dark |
| `TokyoNightLight` | Tokyo Night light |
| `MinLight` | Minimal light |
| `MinDark` | Minimal dark |

The `Theme` enum is from the `phiki/phiki` package. The full list of cases is in `vendor/phiki/phiki/src/Theme/Theme.php`.

### Highlight theme resolution order

1. `theme` attribute on `<x-slidewire::code>` or `<x-slidewire::markdown>`
2. `highlightTheme` from the active `ThemeConfig` (deck or slide theme)
3. `config('slidewire.slides')->highlight->theme`

To set a deck-wide highlight theme without changing the visual theme, use `highlight-theme` on the deck:

```blade
<x-slidewire::deck theme="default" highlight-theme="github-dark">
```

The `highlight-theme` string on the component must be the kebab-case version of the enum case name (e.g. `github-dark` for `GithubDark`), or pass the `Theme::*` via config.
