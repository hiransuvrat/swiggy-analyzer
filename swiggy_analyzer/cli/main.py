"""Main CLI entry point."""

import click
from rich.console import Console

from .commands import auth, sync, analyze, basket, config, schedule


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    Swiggy Instamart Buying Pattern Analyzer

    Analyzes your purchase history and recommends items you're likely to need.
    """
    pass


# Register command groups
cli.add_command(auth)
cli.add_command(sync)
cli.add_command(analyze)
cli.add_command(basket)
cli.add_command(config)
cli.add_command(schedule)


if __name__ == "__main__":
    cli()
