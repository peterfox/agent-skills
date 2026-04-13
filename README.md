# Agent Skills

A collection of Claude Code skills for PHP development workflows.

## Available Skills

| Skill | Description |
|-------|-------------|
| [composer-upgrade](composer-upgrade/) | Upgrading PHP projects with Composer — `outdated`, `why-not`, `bump` |
| [gritql](gritql/) | Writing GritQL patterns for structural code refactoring and migration across languages |
| [laravel-advanced-concepts](laravel-advanced-concepts/) | Advanced Laravel patterns — Feature Flags (Pennant), State Machines (spatie/laravel-model-states), and Event Sourcing (spatie/laravel-event-sourcing, hirethunk/verbs) |
| [npm-upgrade](npm-upgrade/) | Upgrading Node.js projects with npm, yarn, or pnpm — audits, conflicts, lock files |
| [packagist](packagist/) | Searching and looking up PHP packages on Packagist via the API |
| [php-type-safety](php-type-safety/) | PHP type safety using webmozarts/assert and PHPDoc shapes for PHPStan/Psalm |
| [phpstan-developer](phpstan-developer/) | Building PHPStan rules, collectors, and type extensions |
| [rector-developer](rector-developer/) | Building Rector PHP rules for AST-based code transformations |
| [remotion-3d-background-developer](remotion-3d-background-developer/) | Generating procedural 3D backgrounds for Remotion using react-three-fiber and GLSL shaders — liquid gradients, plasma, aurora, galaxy, and geometric/voronoi styles |
| [serpapi](serpapi/) | Searching Google, Google Shopping, Google Jobs, eBay, and Amazon via SerpApi |
| [slidewire-developer](slidewire-developer/) | Building and refining SlideWire presentations in Laravel/Livewire |

## Installing Skills

### Via npx (recommended)

Install all skills from this repo directly into Claude Code:

```bash
npx skills add peterfox/agent-skills
```

Install a single skill by name:

```bash
npx skills add peterfox/agent-skills --skill composer-upgrade
```

### From a release

Download the `.skill` file for the skill you want from the [releases page](https://github.com/peterfox/agent-skills/releases), then install it:

```bash
claude skill install composer-upgrade.skill
```

## Building Locally

Clone the repo and run the packaging script to generate `.skill` files:

```bash
git clone https://github.com/peterfox/agent-skills.git
cd agent-skills
./package-all.sh
```

This requires the [skill-creator](https://github.com/anthropics/claude-code) skill to be installed locally.

## License

[MIT](LICENSE)
