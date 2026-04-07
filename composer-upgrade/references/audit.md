# composer audit — Security Checks and Prioritization

See [commands.md](commands.md) for the full flag reference (`--no-dev`, `--locked`, `--abandoned`, `--ignore-advisories`, etc.). Exit code is non-zero when advisories are found — use this for CI gates.

## Interpreting Output

Each advisory shows:
```
Package: vendor/package
CVE:     CVE-2024-12345 / GHSA-xxxx-yyyy-zzzz
Title:   Remote code execution via X
URL:     https://github.com/advisories/GHSA-xxxx-yyyy-zzzz
Affected versions: >=1.0.0,<1.2.3
```

Severity levels (when shown): **critical**, **high**, **medium**, **low**. Not all advisories include a severity label — check the linked advisory page for CVSS scores.

JSON output via `--format=json` gives structured data suitable for scripting:
```bash
composer audit --format=json | jq '.advisories | to_entries[] | .key, .value[].title'
```

## Prioritizing What to Fix

When you have multiple outdated or vulnerable packages, use this framework to decide what to tackle first:

### Tier 1 — Fix immediately
- Packages with **critical or high** CVEs
- Any package where the advisory describes remote code execution, authentication bypass, or SQL injection
- Packages used in authentication, session handling, or file upload processing

### Tier 2 — Fix in the next maintenance window
- **Medium** severity CVEs
- Packages flagged by audit that also appear in `composer outdated --direct` (two reasons to update = higher priority)
- Abandoned packages with no maintained fork (they won't receive future security patches)

### Tier 3 — Schedule for routine upgrade
- **Low** severity or informational advisories
- Transitive (indirect) dependencies with CVEs where your code doesn't exercise the affected code path
- Outdated but no known CVE

### Building the priority list

Combine audit and outdated output to rank packages:

```bash
# Step 1: Get all advisories
composer audit --format=json > /tmp/audit.json

# Step 2: Get all outdated direct deps
composer outdated --direct --format=json > /tmp/outdated.json

# Step 3: Cross-reference — packages in both lists are highest priority
jq -r '.advisories | keys[]' /tmp/audit.json
```

When reporting to the user, group findings like this:

**Security (fix now)**
- `vendor/package` v1.2.0 — CVE-2024-12345 (critical): Remote code execution — fix: update to >=1.2.3
- `vendor/other` v3.0.0 — CVE-2024-67890 (high): Auth bypass — fix: update to >=3.1.0

**Security + outdated (fix soon)**
- `vendor/framework` v6.0.0 — CVE-2024-11111 (medium) + 3 major versions behind

**Outdated only (routine)**
- `vendor/logger` v1.0.0 → 2.0.0 (major, no CVE)
- `vendor/utils` v2.3.0 → 2.5.0 (minor, no CVE)

## Fixing Vulnerable Packages

For each advisory, the fix is usually to update to a patched version:

```bash
# Check what version fixes it (shown in advisory "Affected versions" field)
composer why-not vendor/package 1.2.3

# If no blocker, update directly
composer update vendor/package --with-all-dependencies --no-interaction --no-progress --no-ansi

# Verify the advisory is resolved
composer audit
```

If a patched version isn't available yet:
- Check if the package is abandoned — if so, find a maintained replacement
- Check if your code actually calls the vulnerable code path (reduces urgency)
- Add a `replace` entry in `composer.json` only as a last resort (for transitive deps with a fork)

## Integrating Audit into the Upgrade Workflow

Run `composer audit` at the **start** of an upgrade session to identify security-driven priorities, and again at the **end** to confirm all advisories are resolved.

For CI, add a failing audit check:
```bash
composer audit --no-dev   # fails build if any production deps have known CVEs
```

To allow specific known advisories temporarily (while a patch is in progress):
```bash
# Check Composer docs for --ignore-advisories (available in Composer 2.6+)
composer audit --ignore-advisories GHSA-xxxx-yyyy-zzzz
```
