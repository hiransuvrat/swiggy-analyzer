"""CLI command implementations."""

import sys
from typing import List

import click
import questionary
from rich.console import Console
from loguru import logger

from ..config.settings import Settings
from ..data.repository import SwiggyRepository
from ..auth.token_store import TokenStore
from ..auth.oauth_manager import OAuthManager
from ..mcp.client import MCPClient
from ..mcp.endpoints import SwiggyInstamartMCP
from ..analysis.pattern_detector import PatternDetector
from ..analysis.scoring import ItemScorer
from ..analysis.predictor import ItemPredictor
from ..basket.manager import BasketManager
from ..basket.formatter import RecommendationFormatter
from ..data.models import ItemRecommendation
from ..scheduler.cron_manager import ScheduleManager
from ..config.defaults import PROJECT_ROOT


console = Console()


def setup_logging(settings: Settings):
    """Setup logging configuration."""
    log_file = settings.get_log_file()
    log_level = settings.get_log_level()

    # Create log directory
    from pathlib import Path
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(
        log_file,
        rotation="10 MB",
        retention="30 days",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    )
    logger.add(sys.stderr, level="WARNING")  # Only show warnings/errors in terminal


def get_services(settings: Settings):
    """Initialize and return all services."""
    # Repository
    repository = SwiggyRepository(settings.get_db_path())

    # Auth
    token_store = TokenStore(repository)
    auth_manager = OAuthManager(token_store)

    # MCP Client
    mcp_client = MCPClient(
        base_url=settings.get_mcp_base_url(),
        auth_manager=auth_manager,
        timeout=settings.get("mcp.timeout"),
        max_retries=settings.get("mcp.retry_attempts"),
        rate_limit=settings.get("mcp.rate_limit"),
    )

    swiggy_mcp = SwiggyInstamartMCP(mcp_client)

    # Analysis
    detector = PatternDetector(repository)
    weights = settings.get("analysis.weights")
    scorer = ItemScorer(
        frequency_weight=weights["frequency"],
        recency_weight=weights["recency"],
        quantity_weight=weights["quantity"],
    )
    predictor = ItemPredictor(detector, scorer)

    # Basket
    basket_manager = BasketManager(swiggy_mcp, repository)
    formatter = RecommendationFormatter()

    return {
        "repository": repository,
        "auth_manager": auth_manager,
        "swiggy_mcp": swiggy_mcp,
        "detector": detector,
        "predictor": predictor,
        "basket_manager": basket_manager,
        "formatter": formatter,
        "mcp_client": mcp_client,
    }


# Auth commands
@click.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
def login():
    """Authenticate with Swiggy MCP."""
    settings = Settings()
    setup_logging(settings)

    console.print("[bold cyan]Swiggy Analyzer - Authentication[/bold cyan]\n")

    services = get_services(settings)
    auth_manager = services["auth_manager"]

    if auth_manager.is_authenticated():
        console.print("[yellow]You are already authenticated.[/yellow]")
        if questionary.confirm("Re-authenticate?").ask():
            auth_manager.logout()
        else:
            return

    console.print("Initiating OAuth authentication...\n")

    if auth_manager.initiate_auth_flow():
        console.print("\n[bold green]✓ Authentication successful![/bold green]")
    else:
        console.print("\n[bold red]✗ Authentication failed.[/bold red]")
        sys.exit(1)


@auth.command()
def logout():
    """Remove authentication tokens."""
    settings = Settings()
    services = get_services(settings)
    auth_manager = services["auth_manager"]

    auth_manager.logout()
    console.print("[green]✓ Logged out successfully[/green]")


@auth.command()
def status():
    """Check authentication status."""
    settings = Settings()
    services = get_services(settings)
    auth_manager = services["auth_manager"]

    if auth_manager.is_authenticated():
        console.print("[green]✓ Authenticated[/green]")
        token_data = services["repository"].get_token(OAuthManager.SERVICE_NAME)
        if token_data and token_data.expires_at:
            console.print(f"Token expires: {token_data.expires_at}")
    else:
        console.print("[red]✗ Not authenticated[/red]")
        console.print("Run: swiggy-analyzer auth login")


# Sync commands
@click.group()
def sync():
    """Data synchronization commands."""
    pass


@sync.command()
@click.option("--full", is_flag=True, help="Full historical sync")
def now(full):
    """Sync order history from Swiggy."""
    settings = Settings()
    setup_logging(settings)

    services = get_services(settings)

    if not services["auth_manager"].is_authenticated():
        console.print("[red]✗ Not authenticated. Run: swiggy-analyzer auth login[/red]")
        sys.exit(1)

    console.print("[cyan]Syncing order history...[/cyan]")

    try:
        days_back = settings.get("sync.full_sync_days") if full else settings.get("sync.incremental_days")

        # Fetch orders
        orders = services["swiggy_mcp"].get_order_history(limit=100, days_back=days_back)

        # Save to database
        services["repository"].save_orders(orders)

        # Calculate patterns
        services["detector"].calculate_patterns()

        order_count = services["repository"].get_order_count()
        item_count = services["repository"].get_item_count()

        console.print(f"[green]✓ Synced {len(orders)} orders[/green]")
        console.print(f"Total orders in database: {order_count}")
        console.print(f"Unique items: {item_count}")

    except Exception as e:
        console.print(f"[red]✗ Sync failed: {e}[/red]")
        logger.exception("Sync failed")
        sys.exit(1)


# Analysis commands
@click.group()
def analyze():
    """Analysis and recommendation commands."""
    pass


@analyze.command()
@click.option("--min-score", type=float, help="Minimum score threshold")
@click.option("--max-items", type=int, help="Maximum items to recommend")
@click.option("--auto-add", is_flag=True, help="Skip confirmation, add all")
@click.option("--dry-run", is_flag=True, help="Simulate without adding to basket")
def run(min_score, max_items, auto_add, dry_run):
    """Run analysis and get recommendations."""
    settings = Settings()
    setup_logging(settings)

    # Use config defaults if not specified
    min_score = min_score or settings.get("analysis.min_score")
    max_items = max_items or settings.get("analysis.max_items")

    services = get_services(settings)

    if not services["auth_manager"].is_authenticated():
        console.print("[red]✗ Not authenticated. Run: swiggy-analyzer auth login[/red]")
        sys.exit(1)

    # Create job log
    job_id = services["repository"].create_job_log("analysis")

    try:
        console.print("[cyan]Analyzing buying patterns...[/cyan]\n")

        # Optional sync
        if settings.get("sync.auto_sync"):
            console.print("[dim]Syncing latest orders...[/dim]")
            try:
                orders = services["swiggy_mcp"].get_order_history(limit=50, days_back=30)
                services["repository"].save_orders(orders)
                services["detector"].calculate_patterns()
            except Exception as e:
                console.print(f"[yellow]⚠ Sync failed, using cached data: {e}[/yellow]\n")

        # Get recommendations
        recommendations = services["predictor"].get_recommendations(min_score, max_items)

        if not recommendations:
            console.print("[yellow]No recommendations at this time.[/yellow]")
            console.print("Try lowering the min-score or adding more order history.")
            services["repository"].update_job_log(job_id, "success", 0, 0)
            return

        # Save recommendations to log
        services["repository"].save_recommendations(recommendations)

        # Validate availability
        console.print("[dim]Checking item availability...[/dim]\n")
        validated = services["basket_manager"].preview_recommendations(recommendations)

        # Show preview
        table = services["formatter"].format_preview(validated)
        console.print(table)
        console.print()

        if dry_run:
            console.print("[yellow]Dry run mode - no items will be added to basket[/yellow]")
            services["repository"].update_job_log(job_id, "success", len(validated), 0)
            return

        # Confirm selection
        selected = validated
        if not auto_add and settings.get("basket.preview_required"):
            selected = confirm_recommendations(validated)

        if not selected:
            console.print("[dim]No items selected.[/dim]")
            services["repository"].update_job_log(job_id, "success", len(validated), 0)
            return

        # Add to basket
        console.print("\n[cyan]Adding items to basket...[/cyan]")
        results = services["basket_manager"].add_items_to_basket(selected)

        # Show summary
        summary = services["formatter"].format_summary(results)
        console.print(summary)

        # Update job log
        services["repository"].update_job_log(
            job_id, "success",
            len(validated),
            len(results["success"])
        )

    except Exception as e:
        console.print(f"\n[red]✗ Analysis failed: {e}[/red]")
        logger.exception("Analysis failed")
        services["repository"].update_job_log(job_id, "failed", 0, 0, str(e))
        sys.exit(1)

    finally:
        services["mcp_client"].close()


def confirm_recommendations(recommendations: List[ItemRecommendation]) -> List[ItemRecommendation]:
    """Interactive selection of recommendations."""
    # Filter only available items
    available = [r for r in recommendations if r.available]

    if not available:
        console.print("[yellow]No items available for selection.[/yellow]")
        return []

    choices = [
        {
            "name": f"{r.item_name} ({r.suggested_quantity}x) - Score: {r.score:.1f}",
            "value": r,
            "checked": True,
        }
        for r in available
    ]

    selected = questionary.checkbox(
        "Select items to add to basket (space to toggle, enter to confirm):",
        choices=choices,
    ).ask()

    return selected if selected else []


# Basket commands
@click.group()
def basket():
    """Basket management commands."""
    pass


@basket.command()
def view():
    """View current basket."""
    settings = Settings()
    setup_logging(settings)

    services = get_services(settings)

    if not services["auth_manager"].is_authenticated():
        console.print("[red]✗ Not authenticated. Run: swiggy-analyzer auth login[/red]")
        sys.exit(1)

    try:
        basket_data = services["basket_manager"].get_basket()

        console.print("[bold cyan]Current Basket[/bold cyan]\n")

        items = basket_data.get("items", [])
        if not items:
            console.print("[dim]Basket is empty[/dim]")
            return

        for item in items:
            console.print(f"• {item.get('name')} ({item.get('quantity')}x) - ₹{item.get('price', 0):.2f}")

        total = basket_data.get("total", 0)
        console.print(f"\n[bold]Total: ₹{total:.2f}[/bold]")

    except Exception as e:
        console.print(f"[red]✗ Failed to get basket: {e}[/red]")
        sys.exit(1)


@basket.command()
def clear():
    """Clear all items from basket."""
    settings = Settings()
    services = get_services(settings)

    if not services["auth_manager"].is_authenticated():
        console.print("[red]✗ Not authenticated. Run: swiggy-analyzer auth login[/red]")
        sys.exit(1)

    if not questionary.confirm("Clear all items from basket?").ask():
        return

    try:
        services["basket_manager"].clear_basket()
        console.print("[green]✓ Basket cleared[/green]")

    except Exception as e:
        console.print(f"[red]✗ Failed to clear basket: {e}[/red]")
        sys.exit(1)


# Config commands
@click.group()
def config():
    """Configuration management."""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
def set_value(key, value):
    """Set configuration value."""
    settings = Settings()

    # Try to parse value
    try:
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.replace(".", "").isdigit():
            value = float(value) if "." in value else int(value)
    except:
        pass

    settings.set(key, value)
    settings.save()

    console.print(f"[green]✓ Set {key} = {value}[/green]")


@config.command()
def show():
    """Show current configuration."""
    settings = Settings()

    console.print("[bold cyan]Current Configuration[/bold cyan]\n")
    import yaml
    console.print(yaml.dump(settings.config, default_flow_style=False))


# Schedule commands
@click.group()
def schedule():
    """Scheduling commands."""
    pass


@schedule.command()
@click.option("--hour", type=int, default=9, help="Hour (0-23)")
@click.option("--minute", type=int, default=0, help="Minute (0-59)")
def enable(hour, minute):
    """Enable daily scheduled analysis."""
    scheduler = ScheduleManager(str(PROJECT_ROOT))

    if scheduler.is_enabled():
        console.print("[yellow]Schedule is already enabled.[/yellow]")
        if not questionary.confirm("Re-configure schedule?").ask():
            return
        scheduler.disable_schedule()

    console.print(f"[cyan]Enabling daily schedule at {hour:02d}:{minute:02d}...[/cyan]")

    if scheduler.enable_schedule(hour, minute):
        console.print(f"[green]✓ Daily schedule enabled for {hour:02d}:{minute:02d}[/green]")

        # Update config
        settings = Settings()
        settings.set("schedule.enabled", True)
        settings.set("schedule.hour", hour)
        settings.set("schedule.minute", minute)
        settings.save()
    else:
        console.print("[red]✗ Failed to enable schedule[/red]")
        sys.exit(1)


@schedule.command()
def disable():
    """Disable scheduled analysis."""
    scheduler = ScheduleManager(str(PROJECT_ROOT))

    if not scheduler.is_enabled():
        console.print("[yellow]Schedule is not enabled.[/yellow]")
        return

    if not questionary.confirm("Disable scheduled analysis?").ask():
        return

    if scheduler.disable_schedule():
        console.print("[green]✓ Schedule disabled[/green]")

        # Update config
        settings = Settings()
        settings.set("schedule.enabled", False)
        settings.save()
    else:
        console.print("[red]✗ Failed to disable schedule[/red]")
        sys.exit(1)


@schedule.command()
def status():
    """Show schedule status."""
    scheduler = ScheduleManager(str(PROJECT_ROOT))

    info = scheduler.get_schedule_info()

    if not info:
        console.print("[dim]Schedule: Not configured[/dim]")
        return

    if info["enabled"]:
        console.print(f"[green]Schedule: Enabled[/green]")
        console.print(f"Daily at: {info['hour']:02d}:{info['minute']:02d}")
    else:
        console.print("[yellow]Schedule: Configured but not loaded[/yellow]")
        console.print(f"Time: {info['hour']:02d}:{info['minute']:02d}")
