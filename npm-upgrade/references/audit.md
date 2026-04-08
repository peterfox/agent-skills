# npm audit — Security Checks and Prioritization

See [commands.md](commands.md) for the full flag reference (`--omit=dev`, `--audit-level`, `--json`, etc.). Exit code is non-zero when vulnerabilities are found at or above the configured level — use this for CI gates.

## Interpreting Output

Each advisory shows:
```
<package>
Severity:    high
Title:       Prototype Pollution in some-package
URL:         https://github.com/advisories/GHSA-xxxx-yyyy-zzzz
Affected:    <1.2.3
Patched in:  >=1.2.3
Dependency:  some-package
```

Severity levels: **critical**, **high**, **moderate**, **low**. The `npm audit --json` output includes `severity`, `url`, `fixAvailable`, and a dependency path for each vulnerability.

**Check if a fix is available:**
```bash
npm audit --json | jq '.vulnerabilities | to_entries[] | {name: .key, severity: .value.severity, fixAvailable: .value.fixAvailable}'
```

`fixAvailable: true` means `npm audit fix` can resolve it. `fixAvailable: { isSemVerMajor: true }` means a fix exists but requires a breaking-change upgrade — use `--force` deliberately.

## Prioritizing What to Fix

When you have multiple vulnerable packages, use this framework:

### Tier 1 — Fix immediately
- **Critical or high** severity advisories
- Any advisory describing remote code execution, authentication bypass, or prototype pollution affecting server-side code
- Packages used in authentication, session handling, or file upload processing

### Tier 2 — Fix in the next maintenance window
- **Moderate** severity
- Packages flagged by audit that also appear in `npm outdated` (two reasons to update = higher priority)
- Packages that `npm audit fix` cannot auto-fix (requires manual version bump or replacement)

### Tier 3 — Schedule for routine upgrade
- **Low** severity or informational advisories
- Vulnerabilities in devDependencies that don't affect production builds
- Transitive dependencies where your code doesn't exercise the vulnerable code path

### Building the priority list

```bash
# Step 1: Get all advisories as JSON
npm audit --json > /tmp/audit.json

# Step 2: Get all outdated direct deps
npm outdated --json > /tmp/outdated.json

# Step 3: Cross-reference — packages in both lists are highest priority
jq '.vulnerabilities | keys[]' /tmp/audit.json
jq 'keys[]' /tmp/outdated.json
```

When reporting to the user, group findings like this:

**Security (fix now)**
- `some-package` v1.2.0 — GHSA-xxxx-yyyy-zzzz (critical): Remote code execution — fix: `npm install some-package@>=1.2.3`
- `other-pkg` v3.0.0 — GHSA-aaaa-bbbb-cccc (high): Prototype pollution — fix: `npm audit fix`

**Security + outdated (fix soon)**
- `framework-pkg` v6.0.0 — GHSA-dddd-eeee-ffff (moderate) + 3 major versions behind

**Outdated only (routine)**
- `some-logger` v1.0.0 → 2.0.0 (major, no CVE)
- `some-util` v2.3.0 → 2.5.0 (minor, no CVE)

## Fixing Vulnerable Packages

**Let npm auto-fix what it can:**
```bash
npm audit fix        # updates within semver constraints
npm audit fix --dry-run   # preview first
```

**For breaking-change fixes, be deliberate:**
```bash
# Check what `--force` would do before running it
npm audit fix --force --dry-run

# Then apply if the breaking changes are acceptable
npm audit fix --force
```

**For packages that can't be auto-fixed:**
```bash
# Install a specific patched version directly
npm install <package>@<patched-version>

# If it's a transitive dep, update the direct dependency that pulls it in
npm explain <vulnerable-package>       # find the direct dep that requires it
npm install <direct-dep>@latest        # update the direct dep to get the fix
```

If a patched version isn't available yet:
- Check if the package is abandoned — if so, find a maintained replacement
- Check if your code actually calls the vulnerable code path (reduces urgency)
- For transitive dependencies you can't update, use [`overrides`](https://docs.npmjs.com/cli/v9/configuring-npm/package-json#overrides) in `package.json` as a last resort to force a patched version

**Override a transitive dep version (last resort):**
```json
{
  "overrides": {
    "vulnerable-transitive-dep": ">=1.2.3"
  }
}
```

Then run `npm install` to apply. Remove the override once the direct dependency pulls in the patched version itself.

## CI Integration

```bash
# Fail the build on any production vulnerability
npm audit --omit=dev

# Fail only on high or critical
npm audit --audit-level=high --omit=dev

# Generate a JSON report for artifact storage
npm audit --json > audit-report.json
```

## Integrating Audit into the Upgrade Workflow

Run `npm audit` at the **start** of an upgrade session to identify security-driven priorities, and again at the **end** to confirm all advisories are resolved.
