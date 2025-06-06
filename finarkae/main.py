"""Main entry point for the Finarkae CLI."""

import typer
from rich.console import Console

from .proxity.cli import app as proxity_app

console = Console()

app = typer.Typer(
    name="finarkae",
    help="Finarkae CLI - a collection of tools for finarkae | by zyme with great 💚.",
    add_completion=False,
)
app.add_typer(proxity_app, name="proxity")


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        from finarkae import __version__

        console.print(f"finarkae-cli version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Finarkae CLI - A collection of tools for finarkae. Made by zyme with great 💚."""
    pass


if __name__ == "__main__":
    app()
