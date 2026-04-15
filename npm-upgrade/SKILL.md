---
name: npm-upgrade
description: Guides Node.js project upgrades using npm, yarn, or pnpm. Use when helping users upgrade npm packages, check for security vulnerabilities with `npm audit`, prioritize which packages to upgrade first, understand dependency conflicts, interpret `npm outdated` output, use `npm explain` to trace who requires a package, plan safe upgrade paths, resolve package version conflicts in package.json, or resolve merge conflicts in package-lock.json / yarn.lock / pnpm-lock.yaml. Trigger this skill whenever the user mentions npm packages, Node.js dependencies, outdated packages, CVEs in JavaScript or TypeScript projects, yarn or pnpm upgrades, or security advisories in package.json.
---

# npm Upgrade

## Approach

Stay focused on **commands and their output**. Your job is to run the right diagnostic commands, interpret what they show, and give a clear upgrade sequence.

**Do not** describe API changes, new syntax, migration steps, or breaking change details for specific packages — no `createRoot` examples, no flat config explanations, no import path changes. That belongs in the package's own migration guide, not here. Stop at "upgrade this package" and let the user read the relevant docs if they need to migrate code.

When you have enough information to recommend a path, recommend it confidently. Don't hedge with a list of options unless the situation genuinely requires a decision from the user.

## Detecting the Package Manager

Check which lock file exists before running commands:

| Lock file | Package manager |
|-----------|----------------|
| `package-lock.json` | `npm` |
| `yarn.lock` | `yarn` |
| `pnpm-lock.yaml` | `pnpm` |

All examples below use `npm`. See [references/commands.md](references/commands.md) for yarn and pnpm equivalents.

## Upgrade Workflow

Follow this sequence when upgrading a Node.js project:

1. **Check for security issues** → `npm audit` — fixes here are highest priority
2. **Try auto-fix** → `npm audit fix` — resolves compatible vulnerabilities automatically
3. **Identify what's outdated** → `npm outdated`
4. **Prioritize** — packages with CVEs AND outdated go first; see [references/audit.md](references/audit.md)
5. **Trace dependencies** → `npm explain <package>` — who requires it and why
6. **Update packages** → `npm update <package>` or `npm install <package>@latest`
7. **Test**
8. **Tighten constraints** → update `package.json` ranges if needed (applications only)
9. **Re-audit** → `npm audit` to confirm all advisories are resolved

See [references/commands.md](references/commands.md) for full flag reference.
See [references/upgrade-workflow.md](references/upgrade-workflow.md) for detailed strategies, including merge conflict resolution.
See [references/audit.md](references/audit.md) for security audit details, severity tiers, and how to build a prioritized fix list.

## Resolving package-lock.json Merge Conflicts

Never edit conflict markers in `package-lock.json` by hand, and avoid blunt `rm package-lock.json && npm install` — that throws away both sides' changes indiscriminately. Instead, use `diff_lock.py` to generate precise npm commands that apply exactly what the other branch changed.

**Preferred approach — apply the other side's changes with npm commands:**

```bash
# 1. Accept one side's package.json as the base (usually your branch)
git checkout --ours package.json

# 2. See what the other branch changed in the lock file
python3 scripts/diff_lock.py --conflict --format=summary

# 3. Get the exact npm commands to apply those changes
python3 scripts/diff_lock.py --conflict

# 4. Run the generated commands (e.g.)
npm install axios@1.7.7
npm install zod@3.23.8
npm uninstall some-removed-package

# 5. Commit
git add package-lock.json package.json
git commit
```

The `--conflict` flag reads both sides of the lock file directly from git — no need to extract markers manually. The default output (without `--format=summary`) produces ready-to-run npm install/uninstall commands for every change.

See [references/upgrade-workflow.md](references/upgrade-workflow.md) — "Workflow: Merge Conflict in package-lock.json" — for the full step-by-step process.

## Core Commands

See [references/commands.md](references/commands.md) for the full flag reference.

### npm outdated

```bash
npm outdated          # tabular view
npm outdated --json   # JSON output for parsing (fewer tokens)
```

Three version columns: **Current** (installed), **Wanted** (latest satisfying package.json range), **Latest** (latest on the registry). A gap between Wanted and Latest means a major bump is available.

### npm explain / npm ls

```bash
npm explain <package>        # who in the tree requires this package
npm explain <package>@1.2.3  # who requires a specific version
npm ls <package>             # show installed versions in the dependency tree
```

### npm update / npm install

```bash
npm update <package>                        # update to latest satisfying package.json range
npm install <package>@latest                # install latest (rewrites package.json entry)
npm install <package>@^2.0.0               # install a specific range
npm install <package>@latest --save-exact   # pin to exact version in package.json
```

### npm audit

```bash
npm audit                # show all vulnerabilities
npm audit fix            # auto-fix compatible vulnerabilities
npm audit fix --force    # also fix via breaking-change upgrades (test carefully)
npm audit --json         # JSON output for scripting
```

## Common Patterns

### "Why can't I update X?"

```bash
# See who requires the package and what version they constrain it to
npm explain <package>
npm ls <package>

# Check what versions exist on the registry
npm view <package> versions --json
```

Run these first, then give a direct recommendation: update the constraining package, relax your own range, or use an override. Pick the right path based on what the output shows — don't list all three as equal options.

### "Safe incremental upgrade"

```bash
# See what would change (no install)
npm outdated

# Patch and minor: update within existing package.json constraints
npm update <package>

# Major: install explicitly, which also rewrites package.json
npm install <package>@latest
```

Prefer updating direct dependencies one at a time, running tests between each. For major version bumps, recommend doing each on its own branch with its own commit — this makes it easy to isolate breakage and revert if needed.

### Relaxing constraints in package.json

When `npm explain` reveals the constraint is in your own `package.json`:

```json
"dependencies": {
    "some-package": "^3.0.0"
}
```

Edit `package.json` then run `npm install` to resolve and update the lock file.

### Pinning constraints after upgrading (applications)

After a successful major upgrade, tighten `package.json` ranges to prevent accidental downgrades on fresh installs:

```bash
# Pin to exact installed version
npm install <package>@latest --save-exact

# Review all direct dep versions before deciding what to pin
npm ls --depth=0
```

> **Applications only**: exact pins (`1.2.3` without `^`) in a library's `package.json` create conflicts for downstream consumers. Libraries should use ranges.
