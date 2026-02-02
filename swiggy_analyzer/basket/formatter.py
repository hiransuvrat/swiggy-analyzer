"""Rich terminal formatting for recommendations."""

from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ..data.models import ItemRecommendation


class RecommendationFormatter:
    """Formats recommendations for terminal display."""

    def __init__(self):
        self.console = Console()

    def format_preview(self, recommendations: List[ItemRecommendation]) -> Table:
        """
        Format recommendations as a Rich table.

        Args:
            recommendations: List of recommendations to display

        Returns:
            Rich Table object
        """
        table = Table(title="🛒 Recommended Items", show_header=True, header_style="bold cyan")

        table.add_column("#", style="dim", width=3)
        table.add_column("Item", style="bold")
        table.add_column("Qty", justify="center", width=5)
        table.add_column("Score", justify="right", width=7)
        table.add_column("Price", justify="right", width=10)
        table.add_column("Reasoning", style="dim")

        for idx, rec in enumerate(recommendations, 1):
            # Score color based on value
            if rec.score >= 80:
                score_style = "bold green"
            elif rec.score >= 60:
                score_style = "yellow"
            else:
                score_style = "dim"

            # Availability indicator
            item_name = rec.item_name
            if not rec.available:
                item_name = f"[dim]{rec.item_name} [red](unavailable)[/red][/dim]"

            # Price
            price_str = f"₹{rec.current_price:.2f}" if rec.current_price else "—"

            table.add_row(
                str(idx),
                item_name,
                str(rec.suggested_quantity),
                f"[{score_style}]{rec.score:.1f}[/{score_style}]",
                price_str,
                rec.reasoning,
            )

        return table

    def format_summary(self, results: Dict[str, Any]) -> Panel:
        """
        Format basket update summary.

        Args:
            results: Dictionary with success/failure information

        Returns:
            Rich Panel with summary
        """
        success_count = len(results.get("success", []))
        failure_count = len(results.get("failed", []))
        total_price = results.get("total_price", 0)

        lines = []
        lines.append(f"[bold]Basket Update Summary[/bold]\n")

        if success_count > 0:
            lines.append(f"[green]✓ Successfully added: {success_count} items[/green]")
            for item in results["success"]:
                lines.append(f"  • {item['name']} ({item['quantity']}x)")

        if failure_count > 0:
            lines.append(f"\n[red]✗ Failed to add: {failure_count} items[/red]")
            for item in results["failed"]:
                lines.append(f"  • {item['name']}: {item['reason']}")

        if total_price > 0:
            lines.append(f"\n[bold cyan]Basket Total: ₹{total_price:.2f}[/bold cyan]")

        text = Text.from_markup("\n".join(lines))
        return Panel(text, border_style="cyan")

    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"[bold red]✗ Error:[/bold red] {message}")

    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"[cyan]ℹ[/cyan] {message}")
