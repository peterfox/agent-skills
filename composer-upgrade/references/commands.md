# Composer Command Reference

## Global Flags for Non-Interactive / Agent Use

Always use these flags when running Composer commands as an agent to suppress progress bars, interactive prompts, and ANSI escape codes:

| Flag | Description |
|------|-------------|
| `--no-interaction` / `-n` | Never ask interactive questions; use defaults. Prevents commands from hanging waiting for input. |
| `--no-progress` | Suppress the download/install progress bar. Reduces noise in `update`, `install`, `require`. |
| `--no-ansi` | Strip ANSI color/formatting codes from output. Produces clean, parseable text. |

**Apply to all mutating commands:**
```bash
composer update vendor/package --no-interaction --no-progress --no-ansi
composer install --no-interaction --no-progress --no-ansi
composer require vendor/package --no-interaction --no-progress --no-ansi
composer bump --no-interaction --no-ansi
```

Read-only commands (`outdated`, `why`, `why-not`, `show`) do not produce progress bars, so `--no-interaction --no-ansi` is sufficient for those. When you will parse the output, add `--format=json` — it produces compact, structured data and avoids color codes and alignment padding, which reduces token use significantly.

---

## composer outdated

Full alias: `composer show --outdated`

| Flag | Description |
|------|-------------|
| `--direct` / `-D` | Only show packages listed in your `composer.json`, not transitive deps |
| `--strict` | Exit with non-zero if any outdated packages found (useful in CI) |
| `--minor-only` | Only show packages with minor updates available |
| `--patch-only` | Only show packages with patch updates available |
| `--locked` | Use versions from `composer.lock` instead of installed |
| `--no-dev` | Exclude `require-dev` packages |
| `--format=json` | JSON output for scripting |
| `--ignore=vendor/pkg` | Skip specific packages (repeatable) |

**Example: Find only direct dependencies with updates:**
```bash
composer outdated --direct
```

**Example: CI check that fails if anything is outdated:**
```bash
composer outdated --strict --exit-code
```

**Example: Get JSON for processing:**
```bash
composer outdated --format=json | jq '.installed[] | select(.latest-status == "semver-safe-update")'
```

---

## composer why-not (alias: composer prohibits)

Diagnoses why a package cannot be upgraded to a given version.

| Flag | Description |
|------|-------------|
| `--recursive` / `-r` | Recursively trace the full dependency chain |
| `--tree` / `-t` | Show as a tree |
| `--format=json` | JSON output for parsing |

**Example: Check what blocks symfony/console 7.0:**
```bash
composer why-not symfony/console 7.0
```

**Example: Check what packages can't support PHP 8.3:**
```bash
composer why-not php 8.3
```

**Interpreting output:**
```
vendor/package  v1.2.0  requires  other/dep (^2.0)
other/dep       v2.5.0  requires  php (^7.4)
```
→ `other/dep` needs updating to allow PHP 8.x before you can upgrade.

---

## composer why (alias: composer depends)

Shows which packages require a given package.

| Flag | Description |
|------|-------------|
| `--recursive` / `-r` | Show full reverse dependency tree |
| `--tree` / `-t` | Display as a tree |
| `--format=json` | JSON output for parsing |

**Example: Find who depends on symfony/http-foundation:**
```bash
composer why symfony/http-foundation
```

---

## composer update

| Flag | Description |
|------|-------------|
| `--with-all-dependencies` | Also update the dependencies of specified packages |
| `--with-dependencies` | Update dependencies of listed packages that are not root requirements |
| `--dry-run` | Simulate without making changes |
| `--no-dev` | Skip `require-dev` packages |
| `--prefer-stable` | Prefer stable versions |
| `--prefer-lowest` | Prefer lowest matching version (useful for CI compat testing) |
| `--lock` | Only update `composer.lock` hash, not packages |
| `--interactive` / `-i` | Interactive package selection |

**Example: Update a package:**
```bash
composer update laravel/framework
```

**Example: Preview what would change:**
```bash
composer update laravel/framework --dry-run
```

**Example: Identify blockers then update with only those specific sub-dependencies:**
```bash
# Identify which packages are blocking laravel/framework 11.0
composer why-not laravel/framework 11.0
# → reveals blocker/one and blocker/two

# Update the target together with its identified blockers
composer update laravel/framework blocker/one blocker/two
```

---

## composer bump

Raises the lower bound of version constraints in `composer.json` to match currently installed versions. Syncs `composer.json` with `composer.lock` while keeping the `^` prefix, so future minor/patch upgrades remain possible.

**For applications only.** Do not run without `--dev-only` on libraries — it narrows constraints in ways that create conflicts for downstream consumers.

| Flag | Description |
|------|-------------|
| `--dev-only` | Only bump `require-dev` constraints (safe on libraries) |
| `--no-dev-only` | Only bump `require` constraints |
| `--dry-run` | Show what would be bumped without changing `composer.json` |

**Example: Before and after**

```
// composer.json before
"phpunit/phpunit": "^9.4"

// composer.json after: composer bump phpunit/phpunit
"phpunit/phpunit": "^9.5.20"
```

**Example: Preview first**
```bash
composer bump --dry-run
```

**Example: Bump only production deps after an update**
```bash
composer update vendor/package --with-all-dependencies
composer bump --no-dev-only
```

**Auto-bump on every update** — add to `composer.json` config for applications:
```json
{
    "config": {
        "bump-after-update": true
    }
}
```
Accepts `true`, `false`, `"dev"`, or `"no-dev"`.

> Note: `composer bump` does not bump platform requirements (`php`, extensions).

---

## composer audit

Checks installed packages against the Packagist security advisories database.

| Flag | Description |
|------|-------------|
| `--no-dev` | Skip `require-dev` packages |
| `--locked` | Check `composer.lock` versions rather than installed |
| `--format=json` | JSON output for scripting |
| `--abandoned` | Also flag abandoned packages (Composer 2.6+) |
| `--ignore-advisories` | Skip specific advisory IDs (Composer 2.6+, repeatable) |

Exit code is non-zero if advisories are found — use in CI to fail builds on vulnerable deps.

**Example: CI security gate (production deps only):**
```bash
composer audit --no-dev
```

**Example: JSON output for scripting:**
```bash
composer audit --format=json | jq '.advisories | keys[]'
```

See [references/audit.md](audit.md) for a full prioritization framework and fix workflow.

---

## composer show

General package inspection tool used alongside upgrade workflows.

```bash
composer show vendor/package                 # show installed version and info
composer show --all vendor/package           # show all available versions
composer show --tree                         # show full dependency tree
composer show --latest                       # show all packages with their latest versions
composer show --format=json vendor/package   # structured output for parsing
composer show --latest --format=json         # all packages + latest versions, parseable
```

---

## Version Constraint Quick Reference

| Constraint | Meaning |
|------------|---------|
| `^1.2.3` | `>=1.2.3 <2.0.0` (most common, allows minor/patch) |
| `~1.2.3` | `>=1.2.3 <1.3.0` (allows patch only) |
| `>=1.0 <2.0` | Explicit range |
| `1.2.*` | Any 1.2.x patch |
| `*` | Any version |
| `dev-main` | A specific branch |

When `why-not` reveals a constraint mismatch, you typically need to either:
1. Widen the constraint in your own `composer.json`
2. Update the package that holds the blocking constraint
