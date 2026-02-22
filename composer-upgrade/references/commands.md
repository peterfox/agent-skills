# Composer Command Reference

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

**Example: Update a package and all of its transitive dependencies:**
```bash
composer update laravel/framework --with-all-dependencies
```

**Example: Preview what would change:**
```bash
composer update laravel/framework --with-all-dependencies --dry-run
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

## composer show

General package inspection tool used alongside upgrade workflows.

```bash
composer show vendor/package        # show installed version and info
composer show --all vendor/package  # show all available versions
composer show --tree                # show full dependency tree
composer show --latest              # show all packages with their latest versions
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
