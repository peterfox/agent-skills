# PHP Project Upgrade Workflows

## Strategy: Incremental vs. Big-Bang

**Incremental** (recommended): Update one package or package group at a time. Test between each update. Easier to isolate breakage.

**Big-bang**: Run `composer update` on everything at once. Faster but harder to debug when things break.

Use incremental for production projects. Big-bang is only reasonable for fresh projects or when all packages are minor/patch updates.

---

## Workflow: PHP Version Upgrade

When upgrading to a new PHP major/minor version (e.g., 8.1 → 8.2):

### 1. Check compatibility

```bash
composer why-not php 8.2
```

This lists every installed package that doesn't declare compatibility with PHP 8.2.

### 2. Triage the blockers

For each blocking package:

```bash
# Check if a newer version supports the target PHP
composer show --all vendor/package | grep -A 20 "requires"

# Or check on Packagist manually
```

Options:
- **Package has a new version**: Update it (`composer update vendor/package --with-all-dependencies`)
- **Package is abandoned**: Find a replacement
- **Package is yours**: Update its `platform` constraint

### 3. Update platform config (optional, for testing)

To test with a specific PHP version requirement without changing system PHP:

```json
// composer.json
{
    "config": {
        "platform": {
            "php": "8.2.0"
        }
    }
}
```

Then run `composer update` to force Composer to resolve for that platform. Remove this after upgrading actual PHP.

### 4. Update PHP constraint in composer.json

```json
"require": {
    "php": "^8.2"
}
```

### 5. Update all packages

```bash
composer update --with-all-dependencies
```

### 6. Bump constraints (application projects)

```bash
composer bump
```

This hardens `composer.json` constraints to the newly installed versions, preventing accidental downgrades on fresh installs.

---

## Workflow: Major Framework Upgrade (e.g., Laravel, Symfony)

### 1. Check what's outdated

```bash
composer outdated --direct
```

### 2. Review framework upgrade guide

Check the official upgrade guide for the framework (e.g., `laravel.com/docs/upgrade`). Note any manual changes to config files, removed APIs, renamed methods.

### 3. Update the framework package

```bash
composer update laravel/framework --with-all-dependencies --dry-run
```

Review the dry-run output. Look for:
- Packages that will be downgraded
- Packages that cannot be resolved

### 4. Resolve conflicts shown by dry-run

For each unresolvable package:

```bash
composer why-not laravel/framework 11.0
```

Update or replace blocking packages, then re-run the dry-run.

### 5. Apply the update

```bash
composer update laravel/framework --with-all-dependencies
```

### 6. Run tests

Run your test suite immediately after each package group update. Don't batch multiple framework upgrades.

### 7. Bump constraints (application projects)

```bash
composer bump
```

Commit the updated `composer.json` alongside `composer.lock`.

---

## Workflow: Audit and Patch Outdated Packages

For routine maintenance (security patches, bug fixes):

### 1. Show only direct, safe updates

```bash
composer outdated --direct
```

Focus on yellow (semver-safe) entries first.

### 2. Batch patch-level updates

```bash
composer outdated --patch-only --direct
```

These are usually safe to update together:

```bash
composer update vendor/pkg1 vendor/pkg2 vendor/pkg3
```

### 3. Handle minor updates individually

Minor updates may contain deprecations or behaviour changes. Update and test one at a time.

### 4. Defer red (major) updates

Major updates need their own upgrade workflow. Note them, but don't include them in routine maintenance.

### 5. Bump after patching (application projects)

```bash
composer bump
```

Run after each batch of updates to lock in the new minimums. Commit alongside `composer.lock`.

---

## Diagnosing Dependency Conflicts

### Symptom: `composer update` fails with a conflict

```
Problem 1
  - Root composer.json requires vendor/a ^2.0
  - vendor/a 2.0.0 requires vendor/b ^1.5
  - vendor/c 3.0.0 requires vendor/b ^2.0
```

### Resolution steps

1. Identify which package is the pivot (vendor/b in this example).
2. Check if a version exists that satisfies both constraints:
   ```bash
   composer show --all vendor/b
   ```
3. If no version satisfies both, one of the requiring packages must be updated or replaced.
4. Use `composer why vendor/b` to see all packages that depend on it:
   ```bash
   composer why vendor/b
   ```

### Symptom: A transitive dependency blocks an upgrade

```bash
composer why-not vendor/target-package 3.0 --recursive
```

The `--recursive` flag traces the full chain so you can find the root constraint to change.

---

## Tips

- Always commit `composer.lock` to version control for application projects (not libraries).
- Run `composer bump` after updates in application projects, and commit `composer.json` alongside `composer.lock`.
- Enable `"bump-after-update": true` in `composer.json` config to automate this for the whole team.
- Run `composer validate` after manual edits to `composer.json`.
- Use `composer audit` to check for known security vulnerabilities in installed packages.
- `composer show --locked` shows what's in the lock file vs. what's installed — useful after merge conflicts.
- When resolving merge conflicts in `composer.lock`, run `composer install` rather than manually editing the lock file.
