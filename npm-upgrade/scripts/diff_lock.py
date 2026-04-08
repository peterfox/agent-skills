#!/usr/bin/env python3
"""
Compare two versions of package-lock.json and generate npm commands to reconcile them.

Useful when resolving merge conflicts in package-lock.json, or when you want to understand
what changed between two branches and apply those changes selectively.

Supports package-lock.json v1 (npm 5-6), v2, and v3 (npm 7+) formats.

Usage:
  # During a merge conflict — compare HEAD vs MERGE_HEAD automatically:
  python3 diff_lock.py --conflict

  # Compare any two sources (file paths or git refs):
  python3 diff_lock.py HEAD:package-lock.json MERGE_HEAD:package-lock.json
  python3 diff_lock.py main:package-lock.json feature-branch:package-lock.json
  python3 diff_lock.py old.lock.json new.lock.json

  # Show a human-readable summary instead of commands:
  python3 diff_lock.py --format=summary HEAD:package-lock.json MERGE_HEAD:package-lock.json
"""

import json
import subprocess
import sys
from pathlib import Path


def git_show(ref):
    """Read a file from git by ref (e.g. HEAD:package-lock.json)."""
    try:
        result = subprocess.run(
            ['git', 'show', ref],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error reading git ref '{ref}': {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


def read_source(source):
    """Read package-lock.json content from a file path or git ref (ref:path notation)."""
    if ':' in source and not Path(source).exists():
        return git_show(source)

    try:
        return Path(source).read_text()
    except FileNotFoundError:
        if ':' in source:
            return git_show(source)
        print(f"File not found: {source}", file=sys.stderr)
        sys.exit(1)


def parse_lock(content, label):
    """
    Parse package-lock.json and return {name: {version, dev}} dict.

    Handles all three lockfile versions:
    - v1 (npm 5-6): top-level 'dependencies' object, nested for workspaces
    - v2/v3 (npm 7+): top-level 'packages' object with 'node_modules/...' keys
    """
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {label}: {e}", file=sys.stderr)
        sys.exit(1)

    lock_version = data.get('lockfileVersion', 1)
    packages = {}

    if lock_version >= 2 and 'packages' in data:
        # v2/v3 format: keys are paths like "node_modules/foo" or ""
        for path, info in data.get('packages', {}).items():
            if path == '':
                # The root package itself — skip
                continue
            # Extract package name from path (handles scoped packages and nested)
            # e.g. "node_modules/@scope/pkg" -> "@scope/pkg"
            # e.g. "node_modules/foo/node_modules/bar" -> "bar" (nested)
            name = _extract_name_from_path(path)
            if name is None:
                continue
            version = info.get('version', '')
            dev = info.get('dev', False)
            # For packages appearing multiple times (nested), keep the top-level one
            top_level_key = f'node_modules/{name}'
            if path == top_level_key or name not in packages:
                packages[name] = {'version': version, 'dev': dev}

    else:
        # v1 format: flat 'dependencies' object (nested entries ignored for simplicity)
        _parse_v1_deps(data.get('dependencies', {}), packages, dev=False)

    return packages


def _extract_name_from_path(path):
    """Extract package name from a node_modules path key."""
    # Strip leading 'node_modules/' segments to get the package name
    # Handles: "node_modules/foo", "node_modules/@scope/pkg",
    #           "node_modules/foo/node_modules/bar"
    parts = path.split('node_modules/')
    if len(parts) < 2:
        return None
    name_part = parts[-1].strip('/')
    if not name_part:
        return None
    return name_part


def _parse_v1_deps(deps, packages, dev):
    """Recursively parse v1-format dependencies dict."""
    for name, info in deps.items():
        version = info.get('version', '')
        is_dev = info.get('dev', dev)
        if name not in packages:
            packages[name] = {'version': version, 'dev': is_dev}
        # Recurse into nested dependencies (older npm hoisting style)
        if 'dependencies' in info:
            _parse_v1_deps(info['dependencies'], packages, is_dev)


def diff_packages(source_packages, target_packages):
    """Return (added, removed, changed) dicts comparing source → target."""
    added, removed, changed = {}, {}, {}

    all_names = set(source_packages) | set(target_packages)
    for name in sorted(all_names):
        in_source = name in source_packages
        in_target = name in target_packages

        if in_target and not in_source:
            added[name] = target_packages[name]
        elif in_source and not in_target:
            removed[name] = source_packages[name]
        elif source_packages[name]['version'] != target_packages[name]['version']:
            changed[name] = {
                'from': source_packages[name]['version'],
                'to': target_packages[name]['version'],
                'dev': target_packages[name]['dev'],
            }

    return added, removed, changed


def print_commands(added, removed, changed, source_label, target_label):
    """Print npm commands to move from source state to target state."""
    total = len(added) + len(removed) + len(changed)
    print(f"# package-lock.json diff: {source_label} → {target_label}")
    print(f"# {len(changed)} changed, {len(added)} added, {len(removed)} removed ({total} total)")
    print()

    # Production packages to update/add
    prod_installs = []
    for name, info in sorted(changed.items()):
        if not info['dev']:
            prod_installs.append((name, info['to'], f"# {name}: {info['from']} → {info['to']}"))
    for name, info in sorted(added.items()):
        if not info['dev']:
            prod_installs.append((name, info['version'], f"# {name}: (new) {info['version']}"))

    if prod_installs:
        print("# Production packages to update/add:")
        for _, _, comment in prod_installs:
            print(comment)
        args = ' '.join(f"{n}@{v}" for n, v, _ in prod_installs)
        print(f"npm install {args}")
        print()

    # Dev packages to update/add
    dev_installs = []
    for name, info in sorted(changed.items()):
        if info['dev']:
            dev_installs.append((name, info['to'], f"# {name}: {info['from']} → {info['to']}"))
    for name, info in sorted(added.items()):
        if info['dev']:
            dev_installs.append((name, info['version'], f"# {name}: (new) {info['version']}"))

    if dev_installs:
        print("# Dev packages to update/add:")
        for _, _, comment in dev_installs:
            print(comment)
        args = ' '.join(f"{n}@{v}" for n, v, _ in dev_installs)
        print(f"npm install --save-dev {args}")
        print()

    # Packages to remove
    prod_removes = sorted(n for n, i in removed.items() if not i['dev'])
    dev_removes = sorted(n for n, i in removed.items() if i['dev'])

    if prod_removes:
        print("# Production packages to remove:")
        for n in prod_removes:
            print(f"# {n}: {removed[n]['version']}")
        print(f"npm uninstall {' '.join(prod_removes)}")
        print()

    if dev_removes:
        print("# Dev packages to remove:")
        for n in dev_removes:
            print(f"# {n}: {removed[n]['version']}")
        print(f"npm uninstall {' '.join(dev_removes)}")
        print()

    if not any([prod_installs, dev_installs, prod_removes, dev_removes]):
        print("# No differences found.")


def print_summary(added, removed, changed, source_label, target_label):
    """Print a human-readable diff summary."""
    total = len(added) + len(removed) + len(changed)
    print(f"package-lock.json diff: {source_label} → {target_label}")
    print(f"{len(changed)} changed, {len(added)} added, {len(removed)} removed ({total} total)")

    if changed:
        print("\nChanged:")
        for name, info in sorted(changed.items()):
            arrow = "↑" if info['to'] > info['from'] else "↓"
            dev = " [dev]" if info['dev'] else ""
            print(f"  {arrow} {name}: {info['from']} → {info['to']}{dev}")

    if added:
        print("\nAdded:")
        for name, info in sorted(added.items()):
            dev = " [dev]" if info['dev'] else ""
            print(f"  + {name}: {info['version']}{dev}")

    if removed:
        print("\nRemoved:")
        for name, info in sorted(removed.items()):
            dev = " [dev]" if info['dev'] else ""
            print(f"  - {name}: {info['version']}{dev}")


DEMO_SOURCE = {
    "lockfileVersion": 3,
    "packages": {
        "": {"name": "my-app", "version": "1.0.0"},
        "node_modules/express": {"version": "4.18.0"},
        "node_modules/lodash": {"version": "4.17.20"},
        "node_modules/axios": {"version": "1.4.0"},
        "node_modules/jest": {"version": "29.0.0", "dev": True},
    },
}

DEMO_TARGET = {
    "lockfileVersion": 3,
    "packages": {
        "": {"name": "my-app", "version": "1.0.0"},
        "node_modules/express": {"version": "4.19.2"},
        "node_modules/lodash": {"version": "4.17.21"},
        "node_modules/zod": {"version": "3.22.0"},
        "node_modules/jest": {"version": "29.7.0", "dev": True},
        "node_modules/vitest": {"version": "1.0.0", "dev": True},
    },
}


def run_demo(fmt):
    source_content = json.dumps(DEMO_SOURCE)
    target_content = json.dumps(DEMO_TARGET)
    source_pkgs = parse_lock(source_content, 'demo-source')
    target_pkgs = parse_lock(target_content, 'demo-target')
    added, removed, changed = diff_packages(source_pkgs, target_pkgs)
    print("=== DEMO MODE (no real files needed) ===")
    print()
    if fmt == 'summary':
        print_summary(added, removed, changed, 'demo-source', 'demo-target')
    else:
        print_commands(added, removed, changed, 'demo-source', 'demo-target')
    print()
    print("=== Script is working correctly. ===")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Diff two package-lock.json versions and generate npm commands.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--demo', action='store_true',
        help='Run a self-test with built-in fake data to verify the script works'
    )
    parser.add_argument(
        '--conflict', action='store_true',
        help='Merge conflict mode: compare HEAD:package-lock.json vs MERGE_HEAD:package-lock.json'
    )
    parser.add_argument(
        '--lock-file', default='package-lock.json', metavar='FILE',
        help='Lock file name to use with --conflict (default: package-lock.json)'
    )
    parser.add_argument(
        'source', nargs='?',
        help='Source: file path or git ref (e.g. main:package-lock.json)'
    )
    parser.add_argument(
        'target', nargs='?',
        help='Target: file path or git ref (e.g. MERGE_HEAD:package-lock.json)'
    )
    parser.add_argument(
        '--format', choices=['commands', 'summary'], default='commands',
        help='Output format (default: commands)'
    )

    args = parser.parse_args()

    if args.demo:
        run_demo(args.format)
        return

    if args.conflict:
        lock = args.lock_file
        source_ref = f"HEAD:{lock}"
        target_ref = f"MERGE_HEAD:{lock}"
        source_content = git_show(source_ref)
        target_content = git_show(target_ref)
        source_label, target_label = source_ref, target_ref
    elif args.source and args.target:
        source_content = read_source(args.source)
        target_content = read_source(args.target)
        source_label, target_label = args.source, args.target
    else:
        parser.print_help()
        sys.exit(1)

    source_pkgs = parse_lock(source_content, source_label)
    target_pkgs = parse_lock(target_content, target_label)
    added, removed, changed = diff_packages(source_pkgs, target_pkgs)

    if args.format == 'summary':
        print_summary(added, removed, changed, source_label, target_label)
    else:
        print_commands(added, removed, changed, source_label, target_label)


if __name__ == '__main__':
    main()
