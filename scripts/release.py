#!/usr/bin/env python3
"""
Automated release script for trxd project.
This script automates the entire release process:
1. Updates version in pyproject.toml
2. Creates git tag
3. Pushes changes
4. GitHub Actions handle the rest automatically
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()
    content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
    pyproject_path.write_text(content)
    print(f"Updated version to {new_version}")


def validate_version(version: str) -> bool:
    """Validate version format (YY.MM.MICRO)."""
    pattern = r'^\d{2}\.\d{2}\.\d+$'
    return bool(re.match(pattern, version))


def get_next_version(current_version: str) -> str:
    """Get next version by incrementing micro version."""
    parts = current_version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {current_version}")

    year, month, micro = parts
    new_micro = int(micro) + 1
    return f"{year}.{month}.{new_micro}"


def main():
    parser = argparse.ArgumentParser(description="Create a new release")
    parser.add_argument(
        "version",
        nargs="?",
        help="Version to release (format: YY.MM.MICRO). If not provided, increments micro version."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )

    args = parser.parse_args()

    current_version = get_current_version()
    print(f"Current version: {current_version}")

    if args.version:
        new_version = args.version
        if not validate_version(new_version):
            print(f"Error: Invalid version format '{new_version}'. Use YY.MM.MICRO format.")
            sys.exit(1)
    else:
        new_version = get_next_version(current_version)

    print(f"New version: {new_version}")

    if args.dry_run:
        print("DRY RUN - Would execute:")
        print(f"1. Update pyproject.toml version to {new_version}")
        print("2. git add pyproject.toml")
        print(f"3. git commit -m 'chore: bump version to {new_version}'")
        print(f"4. git tag -a v{new_version} -m 'Release v{new_version}'")
        print("5. git push origin main")
        print(f"6. git push origin v{new_version}")
        print("7. GitHub Actions will handle changelog and PyPI release")
        return

    # Check if we're on main branch
    result = run_command("git branch --show-current", check=False)
    current_branch = result.stdout.strip()
    if current_branch != "main":
        print(f"Error: Must be on main branch, currently on {current_branch}")
        sys.exit(1)

    # Check if working directory is clean (ignore untracked files)
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        # Check if there are only untracked files
        lines = result.stdout.strip().split('\n')
        tracked_changes = [line for line in lines if not line.startswith('??')]
        if tracked_changes:
            print(
                "Error: Working directory has uncommitted changes. "
                "Please commit or stash changes."
            )
            print("Uncommitted changes:")
            for line in tracked_changes:
                print(f"  {line}")
            sys.exit(1)

    # Update version
    update_version(new_version)

    # Commit version change
    run_command("git add pyproject.toml")
    run_command(f'git commit -m "chore: bump version to {new_version}"')

    # Create and push tag
    run_command(f'git tag -a v{new_version} -m "Release v{new_version}"')
    run_command("git push origin main")
    run_command(f"git push origin v{new_version}")

    print(f"\nRelease v{new_version} created successfully!")
    print("GitHub Actions will now:")
    print("1. Generate and update changelog automatically")
    print("2. Create GitHub release with changelog")
    print("3. Build and publish to PyPI")
    print("\nMonitor progress at: https://github.com/alexmarco/trxd/actions")


if __name__ == "__main__":
    main()
