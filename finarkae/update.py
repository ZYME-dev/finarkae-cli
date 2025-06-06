"""Self-update functionality for finarkae CLI."""

import subprocess
import urllib.error
import urllib.request

import typer
from rich.console import Console

from ._version import __version__

console = Console()

# GitHub repository URL
REPO_URL = "https://github.com/zyme-dev/finarkae-cli.git"
# GitHub raw content URL for VERSION file
VERSION_URL = "https://raw.githubusercontent.com/zyme-dev/finarkae-cli/main/VERSION"


def get_latest_version_from_github() -> str | None:
    """Get the latest version from GitHub by fetching the VERSION file."""
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=30) as response:
            if response.status == 200:
                content = response.read().decode("utf-8").strip()
                return content
            return None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        console.print(f"[dim]Debug: Failed to fetch version: {e}[/dim]")
        return None


def compare_versions(current: str, latest: str) -> bool:
    """Compare version strings. Returns True if latest > current."""
    try:
        # Simple version comparison for semantic versioning
        # Split by dots and compare each part as integer
        current_parts = [int(x) for x in current.split(".")]
        latest_parts = [int(x) for x in latest.split(".")]

        # Pad shorter version with zeros
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))

        for cp, lp in zip(current_parts, latest_parts):
            if lp > cp:
                return True
            elif lp < cp:
                return False

        return False  # Versions are equal

    except ValueError:
        # If version parsing fails, assume update is needed
        return True


def update_from_repo() -> bool:
    """Update finarkae CLI from the GitHub repository using uv tool install."""
    try:
        console.print("[yellow]Updating finarkae CLI...[/yellow]")

        # Run uv tool install with --force flag to update
        result = subprocess.run(
            ["uv", "tool", "install", f"git+{REPO_URL}", "--force"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            console.print("[green]✅ Update completed successfully![/green]")
            return True
        else:
            console.print("[red]❌ Update failed:[/red]")
            console.print(f"[red]{result.stderr}[/red]")
            return False

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
        console.print(f"[red]❌ Update failed: {e}[/red]")
        return False


def update():
    """Update finarkae CLI to the latest version from GitHub repository."""
    console.print("[cyan]🔍 Checking for updates...[/cyan]")

    current_version = __version__
    console.print(f"Current version: [blue]{current_version}[/blue]")

    # Get latest version from GitHub
    latest_version = get_latest_version_from_github()

    if latest_version is None:
        console.print("[red]❌ Could not check for updates. Please check your internet connection and try again.[/red]")
        raise typer.Exit(1)

    console.print(f"Latest version:  [blue]{latest_version}[/blue]")

    # Compare versions
    if not compare_versions(current_version, latest_version):
        console.print("[green]✅ You are already running the latest version![/green]")
        return

    console.print(f"[yellow]📦 New version available: {current_version} → {latest_version}[/yellow]")

    # Ask for confirmation
    if not typer.confirm("Would you like to update now?"):
        console.print("[yellow]Update cancelled.[/yellow]")
        return

    # Perform update
    if update_from_repo():
        console.print(f"[green]🎉 Successfully updated from {current_version} to {latest_version}![/green]")
        console.print("[dim]You may need to restart your terminal or run 'hash -r' to refresh the command cache.[/dim]")
    else:
        console.print("[red]❌ Update failed. Please try updating manually:[/red]")
        console.print(f"[dim]uv tool install {REPO_URL} --force[/dim]")
        raise typer.Exit(1)
