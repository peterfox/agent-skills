# npm Command Reference

## Flags for Non-Interactive / Agent Use

npm is generally non-interactive by default, but use these flags when running as an agent:

| Flag | Description |
|------|-------------|
| `--json` | Structured JSON output — use when parsing results; avoids color codes and alignment padding |
| `--no-progress` | Suppress progress bars (npm 7+) |
| `--yes` / `-y` | Accept prompts automatically (e.g. `npm init -y`) |
| `--loglevel=error` | Suppress informational output; show only errors |
| `--prefer-offline` | Use cached packages when possible |

**Prefer `--json` for read commands** when you will parse the output. It reduces token use significantly and avoids reformatting issues.

---

## npm outdated

Shows packages with newer versions available.

| Flag | Description |
|------|-------------|
| `--json` | JSON output for scripting |
| `--depth=N` | How deep to check transitive deps (default: 0 for direct only) |
| `--global` / `-g` | Check globally installed packages |
| `--omit=dev` | Exclude devDependencies |

**Output columns:**
- **Current**: installed version
- **Wanted**: latest version satisfying your `package.json` constraint
- **Latest**: latest published on the registry

A gap between Wanted and Latest signals a major version is available.

**Example: Parse JSON for scripting:**
```bash
npm outdated --json | jq 'to_entries[] | {package: .key, current: .value.current, latest: .value.latest}'
```

**Example: Check only direct deps:**
```bash
npm outdated --depth=0
```

---

## npm explain (alias: npm why)

Shows why a package is installed — which packages in the tree require it, and what version constraints they place on it.

```bash
npm explain <package>          # all installed versions of the package
npm explain <package>@<ver>    # a specific version
npm explain <package> --json   # JSON output
```

To understand why a package can't be upgraded, combine this with `npm view <pkg> versions` to find a version that satisfies all constraints, or identify which direct dependency needs updating first.

---

## npm ls (alias: npm list)

Shows the full installed dependency tree.

```bash
npm ls                        # full tree
npm ls --depth=0              # direct dependencies only
npm ls <package>              # show where a specific package appears in the tree
npm ls --json                 # JSON output
npm ls --json --depth=0       # direct deps as JSON
npm ls --omit=dev             # production deps only
```

---

## npm update

Updates packages to the latest version satisfying the range in `package.json`. Does **not** change `package.json` version ranges.

| Flag | Description |
|------|-------------|
| `--save` | Update `package.json` range to match installed (npm 8+) |
| `--dry-run` | Preview what would change |
| `--omit=dev` | Skip devDependencies |

```bash
npm update <package>                     # update to latest within constraint
npm update <package> --dry-run           # preview
npm update                               # update all (within constraints)
```

To update beyond the current constraint (i.e. a major bump), use `npm install`:
```bash
npm install <package>@latest             # resolves latest, rewrites package.json entry
npm install <package>@^3.0.0            # specific range
npm install <package>@latest --save-exact  # pin to exact version
```

---

## npm install

Install or update specific packages. Unlike `npm update`, `npm install <pkg>@version` rewrites `package.json`.

```bash
npm install <package>@latest            # install latest, update package.json
npm install <package>@^3.0.0           # install range, update package.json
npm install <package>@latest --save-exact  # install latest, pin exact version
npm install --save-dev <package>@latest    # update devDependency
npm install                             # install from package-lock.json
```

---

## npm audit

Checks installed packages against the npm security advisory database.

| Flag | Description |
|------|-------------|
| `--json` | JSON output for scripting |
| `--omit=dev` | Production deps only |
| `--audit-level=<level>` | Only report at or above this severity (`info`, `low`, `moderate`, `high`, `critical`) |
| `--dry-run` | With `fix`: preview without changing anything |

Exit code is non-zero when vulnerabilities at or above `--audit-level` are found — use in CI to fail builds.

```bash
npm audit                         # show all advisories
npm audit fix                     # auto-fix compatible upgrades
npm audit fix --force             # fix including breaking-change upgrades
npm audit --omit=dev              # production-only CI gate
npm audit --audit-level=high      # fail only on high/critical
npm audit --json | jq '.vulnerabilities | to_entries[] | .key'
```

See [audit.md](audit.md) for a prioritization framework and fix workflow.

---

## npm view (alias: npm info, npm show)

Inspect registry metadata for a package — useful when diagnosing why an upgrade is blocked.

```bash
npm view <package>                     # all metadata
npm view <package> versions            # all published versions as array
npm view <package> versions --json     # same, as JSON
npm view <package> peerDependencies    # peer deps for the latest version
npm view <package>@<ver> engines       # Node.js engine requirements for a version
```

---

## npm dedupe

Simplifies the dependency tree by deduplicating packages that appear multiple times.

```bash
npm dedupe           # flatten where possible
npm dedupe --dry-run # preview
```

Run this after a series of updates to reduce duplication before committing.

---

## Version Constraint Quick Reference

| Constraint | Meaning |
|------------|---------|
| `^1.2.3` | `>=1.2.3 <2.0.0` — allows minor and patch (most common) |
| `~1.2.3` | `>=1.2.3 <1.3.0` — allows patch only |
| `1.2.3` | Exact version, no upgrades |
| `>=1.0.0 <2.0.0` | Explicit range |
| `1.2.x` | Any 1.2.* patch |
| `*` | Any version |
| `latest` | Resolves to current dist-tag |

When `npm explain` reveals a constraint mismatch, you typically need to either:
1. Widen the constraint in your own `package.json`
2. Update the package that holds the blocking constraint

---

## yarn Equivalents

| npm | yarn |
|-----|------|
| `npm outdated` | `yarn outdated` |
| `npm audit` | `yarn audit` |
| `npm audit fix` | `yarn upgrade <pkg>` (no auto-fix; fix manually) |
| `npm install <pkg>@latest` | `yarn upgrade <pkg> --latest` |
| `npm update <pkg>` | `yarn upgrade <pkg>` |
| `npm explain <pkg>` | `yarn why <pkg>` |
| `npm ls` | `yarn list` |
| `npm dedupe` | `yarn dedupe` (yarn 2+) |

---

## pnpm Equivalents

| npm | pnpm |
|-----|------|
| `npm outdated` | `pnpm outdated` |
| `npm audit` | `pnpm audit` |
| `npm audit fix` | `pnpm audit --fix` |
| `npm install <pkg>@latest` | `pnpm update <pkg> --latest` |
| `npm update <pkg>` | `pnpm update <pkg>` |
| `npm explain <pkg>` | `pnpm why <pkg>` |
| `npm ls` | `pnpm list` |
| `npm dedupe` | `pnpm dedupe` |
