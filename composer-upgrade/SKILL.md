---
name: composer-upgrade
description: Guides PHP project upgrades using Composer commands. Use when helping users upgrade PHP packages, check for security vulnerabilities with `composer audit`, prioritize which packages to upgrade first, understand dependency conflicts, interpret `composer outdated` output, use `composer why-not` to diagnose version constraints, use `composer why` to trace dependencies, use `composer bump` to harden version constraints after upgrading, plan safe upgrade paths, resolve package version conflicts in composer.json, or resolve merge conflicts in composer.lock. Trigger this skill whenever the user mentions composer packages, PHP dependencies, outdated packages, CVEs in PHP projects, or security advisories.
---

# Composer Upgrade

## Upgrade Workflow

Follow this sequence when upgrading a PHP project:

1. **Check for security issues** → `composer audit` — fixes here are highest priority
2. **Identify what's outdated** → `composer outdated --format=json`
3. **Prioritize** — packages with CVEs AND outdated go first; see [references/audit.md](references/audit.md)
4. **Diagnose blockers** → `composer why-not vendor/package version`
5. **Trace dependencies** → `composer why vendor/package`
6. **Update packages** → `composer update vendor/package --with-all-dependencies`
7. **Test**
8. **Harden constraints** → `composer bump` (applications only)
9. **Re-audit** → `composer audit` to confirm all advisories are resolved

See [references/commands.md](references/commands.md) for full flag reference, including global flags for non-interactive use (`--no-interaction --no-progress --no-ansi`).
See [references/upgrade-workflow.md](references/upgrade-workflow.md) for detailed strategies, including merge conflict resolution.
See [references/audit.md](references/audit.md) for security audit details, severity tiers, and how to build a prioritized package list.

## Resolving composer.lock Merge Conflicts

When `composer.lock` has a merge conflict, use `scripts/diff_lock.py` to compare both sides and generate the commands needed to reconcile them.

**During an active merge conflict:**

```bash
# Compare HEAD vs MERGE_HEAD automatically and output composer commands
python3 scripts/diff_lock.py --conflict

# Human-readable summary of what changed
python3 scripts/diff_lock.py --conflict --format=summary
```

**Compare any two branches or files:**

```bash
python3 scripts/diff_lock.py main:composer.lock feature-branch:composer.lock
python3 scripts/diff_lock.py HEAD:composer.lock MERGE_HEAD:composer.lock
python3 scripts/diff_lock.py old.lock new.lock
```

The script outputs `composer require` / `composer remove` commands that move packages from the source state to the target state. Run the generated commands, then commit the result.

See [references/upgrade-workflow.md](references/upgrade-workflow.md) — "Workflow: Merge Conflict in composer.lock" — for the full step-by-step process.

## Core Commands

### composer outdated

Lists packages with newer versions available.

```bash
composer outdated --format=json           # preferred when parsing output (fewer tokens)
composer outdated --direct --format=json  # only packages in require/require-dev
composer outdated symfony/*               # filter by pattern
composer outdated                         # plain text (for display to user only)
```

**Reading the output:**
- **Red** = semver major bump (breaking changes likely)
- **Yellow** = semver minor/patch (safe upgrade)
- `!` marker = package is not semver-safe (minor/patch but breaking)

Columns: `name | current | latest | description`

### composer why-not

Shows what prevents upgrading a package to a specific version.

```bash
composer why-not vendor/package 2.0
composer why-not php 8.2            # check what blocks a PHP version requirement
composer why-not vendor/package "*" # check what blocks any upgrade
```

Output shows the dependency chain: which packages require conflicting versions.

### composer why

Shows which installed packages depend on a given package.

```bash
composer why vendor/package
composer why-not vendor/package     # inverse: what conflicts with it
```

### composer update

```bash
composer update                                                                        # update all (risky on large projects)
composer update vendor/package --no-interaction --no-progress --no-ansi               # update one package
composer update vendor/package --with-all-dependencies --no-interaction --no-progress --no-ansi  # also update its deps
composer update --dry-run --no-interaction --no-ansi                                  # preview changes without applying
```

## Common Patterns

### "Why can't I update X?"

```bash
composer why-not vendor/package 3.0
```

Read the output to find which package constrains it, then check if that constraining package itself can be updated.

### "What's blocking my PHP version upgrade?"

```bash
composer why-not php 8.2
```

Lists every package that lacks a `php: ^8.2` constraint, sorted by most blocking.

### "Safe incremental upgrade"

Prefer updating direct dependencies one at a time with `--dry-run` first:

```bash
composer update vendor/package --with-all-dependencies --dry-run --no-interaction --no-ansi
composer update vendor/package --with-all-dependencies --no-interaction --no-progress --no-ansi
```

### Relaxing constraints in composer.json

When `why-not` reveals a constraint in your own `composer.json`, update the version constraint and re-run:

```json
"require": {
    "vendor/package": "^3.0"   // was "^2.0"
}
```

Then: `composer update vendor/package`

### Hardening constraints after upgrading (applications)

After updating packages in an application, run `composer bump` to raise the lower bounds of constraints in `composer.json` to the currently installed versions:

```bash
composer bump                  # harden all constraints
composer bump vendor/package   # harden one package
composer bump --dev-only       # only require-dev (safe for libraries too)
```

Before: `"symfony/console": "^6.0"` → After: `"symfony/console": "^6.4.3"`

This prevents future `composer install` runs from resolving older versions that weren't tested. It does **not** prevent future minor/patch upgrades — the `^` is preserved.

**Enable auto-bump in `composer.json` for applications:**

```json
{
    "config": {
        "bump-after-update": true
    }
}
```

With this set, Composer automatically runs `bump` after every `composer update`. Use `"dev"` or `"no-dev"` to limit which dependency group is bumped.

> **Applications only**: Do not run `composer bump` (without `--dev-only`) on libraries. Narrowing lower bounds of library dependencies causes version conflicts for downstream consumers.
