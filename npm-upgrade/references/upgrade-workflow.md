# Node.js Project Upgrade Workflows

## Strategy: Incremental vs. Big-Bang

**Incremental** (recommended): Update one package or package group at a time. Run tests between each update. Easier to isolate breakage.

**Big-bang**: `npm update` on everything at once. Faster but harder to debug when something breaks.

Use incremental for production projects. Big-bang is reasonable only for fresh projects or when all updates are patch-level.

---

## Workflow: Node.js Version Upgrade

When upgrading to a new Node.js major version (e.g., 18 → 20):

### 1. Check what packages declare engine constraints

```bash
npm ls --json | jq '.. | .engines? // empty | select(has("node"))'
```

Or look for packages with a narrow `engines.node` field:
```bash
for dir in node_modules/*/; do
  node -e "const p=require('./$dir/package.json'); if(p.engines?.node) console.log('$dir', p.engines.node)"
done
```

### 2. Update the engines field in your package.json

```json
{
  "engines": {
    "node": ">=20.0.0"
  }
}
```

### 3. Check for deprecated APIs

Run your tests on the new Node.js version. Common breaking changes:
- `--openssl-legacy-provider` flag removed
- Changes to `fs`, `http`, `crypto` modules
- Updated V8 version (affects some native addons)

### 4. Update packages that had old engine constraints

```bash
npm outdated --depth=0
npm install <package>@latest   # for packages needing updates
```

### 5. Run tests and fix compatibility issues

---

## Workflow: Major Package Upgrade (e.g., React, Next.js, Express)

### 1. Check what's outdated

```bash
npm outdated --depth=0   # direct deps only
```

### 2. Review the package's upgrade guide

Check the official migration/upgrade guide before starting. Note manual changes required to config files, renamed APIs, or removed exports.

### 3. Preview what would change

```bash
npm install <package>@latest --dry-run
```

Review the output. Look for:
- Packages that would be downgraded
- Unresolved peer dependencies

### 4. Resolve peer dependency conflicts

```bash
npm explain <blocked-package>   # see who requires conflicting versions
npm view <package> peerDependencies   # see what peers the new version requires
```

Options:
- Update the peer to a compatible version first
- Use `--legacy-peer-deps` temporarily during transition (avoid long-term)
- Use `overrides` in `package.json` if a transitive peer dep needs forcing

### 5. Apply the update

```bash
npm install <package>@latest
```

### 6. Run tests

Run your test suite immediately. Don't batch multiple major upgrades together.

### 7. Tighten constraints if needed (applications)

After confirming the upgrade works, update `package.json` ranges to reflect the new minimum:
```json
"dependencies": {
    "react": "^18.0.0"
}
```

---

## Workflow: Audit and Patch Outdated Packages

For routine maintenance (security patches, bug fixes):

### 1. Run audit first

```bash
npm audit
npm audit fix   # apply compatible fixes automatically
```

### 2. Show outdated direct deps

```bash
npm outdated --depth=0
```

### 3. Batch patch-level updates

These are usually safe to group:

```bash
npm update <pkg1> <pkg2> <pkg3>   # updates within existing constraints
```

### 4. Handle minor updates individually

Minor updates may contain deprecations or behavior changes. Update and test one at a time.

### 5. Defer major updates

Major updates need their own upgrade workflow. Note them, but don't mix them into routine maintenance.

---

## Diagnosing Dependency Conflicts

### Symptom: conflicting peer dependencies

```
npm warn ERESOLVE overriding peer dependency
npm error code ERESOLVE
npm error ERESOLVE could not resolve
```

### Resolution steps

1. Identify which package is the conflict point:
   ```bash
   npm explain <conflicting-package>
   ```

2. Check if a version exists that satisfies both requirements:
   ```bash
   npm view <conflicting-package> versions --json
   ```

3. Update the most constraining direct dependency first:
   ```bash
   npm install <direct-dep>@latest
   ```

4. If still blocked, use `overrides` in `package.json` as a last resort:
   ```json
   {
     "overrides": {
       "conflicting-package": "^3.0.0"
     }
   }
   ```
   Remove the override once the direct dependencies are updated to accept compatible versions naturally.

### Symptom: a transitive dependency blocks an upgrade

```bash
npm explain <package>    # find who is constraining it
npm ls <package>         # see all installed versions in the tree
```

Find the direct dependency that pulls in the old version, then update that direct dependency.

---

## Workflow: Merge Conflict in package-lock.json

`package-lock.json` is auto-generated, so merge conflicts should be resolved by regeneration rather than manual editing.

### Quick resolution (recommended)

```bash
# 1. Choose which package.json to use (usually the more up-to-date branch)
git checkout --theirs package.json   # or --ours

# 2. See what changed in the lock file between the two branches
python3 scripts/diff_lock.py --conflict --format=summary

# 3. Regenerate the lock file cleanly
rm package-lock.json
npm install

# 4. Commit
git add package-lock.json package.json
git commit
```

### When you need to understand the delta first

```bash
# Summarise what changed between the two branches' lock files
python3 scripts/diff_lock.py HEAD:package-lock.json MERGE_HEAD:package-lock.json --format=summary

# Generate npm commands to move selectively from one state to another
python3 scripts/diff_lock.py HEAD:package-lock.json MERGE_HEAD:package-lock.json
```

### How the diff script works

`scripts/diff_lock.py` reads both sides of the lock file from git (no need to extract conflict markers manually), diffs the package entries, and outputs:
- `npm install <pkg>@<version>` for version changes and new packages
- `npm uninstall <pkg>` for removed packages

It groups prod and dev packages separately and annotates each line with the old→new version.

### yarn.lock conflicts

yarn.lock conflicts follow the same principle — regenerate rather than edit:

```bash
git checkout --theirs package.json
rm yarn.lock
yarn install
git add yarn.lock package.json
git commit
```

### pnpm-lock.yaml conflicts

```bash
git checkout --theirs package.json
rm pnpm-lock.yaml
pnpm install
git add pnpm-lock.yaml package.json
git commit
```

---

## Tips

- Always commit `package-lock.json` (or `yarn.lock` / `pnpm-lock.yaml`) to version control for application projects. Libraries typically gitignore lock files.
- Run `npm dedupe` after a series of updates to flatten the tree and reduce duplication.
- Use `npm ls --depth=0` to get a clean view of your direct dependencies and their installed versions.
- When you use `overrides` to force a transitive dep version, leave a comment in `package.json` explaining why, and plan to remove it once the direct dependency is updated.
- `npm install` (no arguments) installs from the lock file — it won't resolve conflicts. You need `npm install <pkg>@<ver>` to change versions.
- For monorepos using workspaces, prefix commands with `-w <workspace>` to target a specific package: `npm install <pkg>@latest -w packages/my-app`.
