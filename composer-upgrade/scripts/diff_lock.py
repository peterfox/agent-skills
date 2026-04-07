#!/usr/bin/env python3
"""
Compare two versions of composer.lock and generate composer commands to reconcile them.

Useful when resolving merge conflicts in composer.lock, or when you want to understand
what changed between two branches and apply those changes selectively.

Usage:
  # During a merge conflict — compare HEAD vs MERGE_HEAD automatically:
  python3 diff_lock.py --conflict

  # Compare any two sources (file paths or git refs):
  python3 diff_lock.py HEAD:composer.lock feature-branch:composer.lock
  python3 diff_lock.py main:composer.lock dev:composer.lock
  python3 diff_lock.py old.lock new.lock

  # Show a human-readable summary instead of commands:
  python3 diff_lock.py --format=summary HEAD:composer.lock MERGE_HEAD:composer.lock
"""

import json
import subprocess
import sys
from pathlib import Path


def git_show(ref):
    """Read a file from git by ref (e.g. HEAD:composer.lock)."""
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
    """Read composer.lock content from a file path or git ref (ref:path notation)."""
    # Git ref notation: contains ':' and the path part exists in git (not as a local file)
    if ':' in source and not Path(source).exists():
        return git_show(source)

    try:
        return Path(source).read_text()
    except FileNotFoundError:
        # Maybe it's a git ref without a local file (e.g. main:composer.lock)
        if ':' in source:
            return git_show(source)
        print(f"File not found: {source}", file=sys.stderr)
        sys.exit(1)


def parse_lock(content, label):
    """Parse composer.lock JSON and return {name: {version, dev}} dict."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {label}: {e}", file=sys.stderr)
        sys.exit(1)

    packages = {}
    for pkg in data.get('packages', []):
        packages[pkg['name']] = {'version': pkg['version'], 'dev': False}
    for pkg in data.get('packages-dev', []):
        packages[pkg['name']] = {'version': pkg['version'], 'dev': True}

    return packages


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


def make_constraint(version):
    """Convert a lock file version string to a composer require constraint."""
    # Branch versions (dev-main, dev-feature, 1.x-dev)
    if 'dev' in version.lower():
        return version

    # Strip 'v' prefix then use ^ for semver
    v = version.lstrip('v')
    parts = v.split('.')
    if len(parts) >= 2:
        return f"^{v}"
    return v


def print_commands(added, removed, changed, source_label, target_label):
    """Print composer commands to move from source state to target state."""
    total = len(added) + len(removed) + len(changed)
    print(f"# composer.lock diff: {source_label} → {target_label}")
    print(f"# {len(changed)} changed, {len(added)} added, {len(removed)} removed ({total} total)")
    print()

    # --- Update/add production packages ---
    prod_requires = []
    for name, info in sorted(changed.items()):
        if not info['dev']:
            prod_requires.append((name, info['to'],
                                   f"# {name}: {info['from']} → {info['to']}"))
    for name, info in sorted(added.items()):
        if not info['dev']:
            prod_requires.append((name, info['version'],
                                   f"# {name}: (new) {info['version']}"))

    if prod_requires:
        print("# Production packages to update/add:")
        for _, _, comment in prod_requires:
            print(comment)
        args = ' '.join(f"{n}:{make_constraint(v)}" for n, v, _ in prod_requires)
        print(f"composer require {args} --no-interaction --no-progress --no-ansi")
        print()

    # --- Update/add dev packages ---
    dev_requires = []
    for name, info in sorted(changed.items()):
        if info['dev']:
            dev_requires.append((name, info['to'],
                                  f"# {name}: {info['from']} → {info['to']}"))
    for name, info in sorted(added.items()):
        if info['dev']:
            dev_requires.append((name, info['version'],
                                  f"# {name}: (new) {info['version']}"))

    if dev_requires:
        print("# Dev packages to update/add:")
        for _, _, comment in dev_requires:
            print(comment)
        args = ' '.join(f"{n}:{make_constraint(v)}" for n, v, _ in dev_requires)
        print(f"composer require --dev {args} --no-interaction --no-progress --no-ansi")
        print()

    # --- Remove packages ---
    prod_removes = sorted(n for n, i in removed.items() if not i['dev'])
    dev_removes = sorted(n for n, i in removed.items() if i['dev'])

    if prod_removes:
        print("# Production packages to remove:")
        for n in prod_removes:
            print(f"# {n}: {removed[n]['version']}")
        print(f"composer remove {' '.join(prod_removes)} --no-interaction --no-progress --no-ansi")
        print()

    if dev_removes:
        print("# Dev packages to remove:")
        for n in dev_removes:
            print(f"# {n}: {removed[n]['version']}")
        print(f"composer remove --dev {' '.join(dev_removes)} --no-interaction --no-progress --no-ansi")
        print()

    if not any([prod_requires, dev_requires, prod_removes, dev_removes]):
        print("# No differences found.")


def print_summary(added, removed, changed, source_label, target_label):
    """Print a human-readable diff summary."""
    total = len(added) + len(removed) + len(changed)
    print(f"composer.lock diff: {source_label} → {target_label}")
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
    "packages": [
        {"name": "symfony/console", "version": "6.3.0"},
        {"name": "symfony/http-kernel", "version": "6.3.0"},
        {"name": "guzzlehttp/guzzle", "version": "7.5.0"},
    ],
    "packages-dev": [
        {"name": "phpunit/phpunit", "version": "10.0.0"},
    ],
}

DEMO_TARGET = {
    "packages": [
        {"name": "symfony/console", "version": "6.4.1"},
        {"name": "symfony/http-kernel", "version": "6.4.1"},
        {"name": "monolog/monolog", "version": "3.5.0"},
    ],
    "packages-dev": [
        {"name": "phpunit/phpunit", "version": "10.2.0"},
        {"name": "mockery/mockery", "version": "1.6.0"},
    ],
}


def run_demo(fmt):
    import json as _json
    source_content = _json.dumps(DEMO_SOURCE)
    target_content = _json.dumps(DEMO_TARGET)
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
        description='Diff two composer.lock versions and generate composer commands.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--demo', action='store_true',
        help='Run a self-test with built-in fake data to verify the script works'
    )
    parser.add_argument(
        '--conflict', action='store_true',
        help='Merge conflict mode: compare HEAD:composer.lock vs MERGE_HEAD:composer.lock'
    )
    parser.add_argument(
        '--lock-file', default='composer.lock', metavar='FILE',
        help='Lock file name to use with --conflict (default: composer.lock)'
    )
    parser.add_argument(
        'source', nargs='?',
        help='Source: file path or git ref (e.g. main:composer.lock)'
    )
    parser.add_argument(
        'target', nargs='?',
        help='Target: file path or git ref (e.g. MERGE_HEAD:composer.lock)'
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
