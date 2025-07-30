"""Main CLI entry point for ytnote."""

import typer
from rich.console import Console

from ytnote.config import settings

console = Console()
app = typer.Typer(
    name="ytnote", help="A tool to download YouTube captions and generate summaries", rich_markup_mode="rich"
)


@app.command()
def fetch(
    url: str = typer.Argument(..., help="YouTube URL to fetch transcript from"),
    lang: str = typer.Option("en", "--lang", "-l", help="Preferred transcript language"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-fetch even if cached"),
    outdir: str = typer.Option(None, "--outdir", "-o", help="Output directory (overrides config)"),
) -> None:
    """Fetch transcript for a YouTube video."""
    console.print(f"[bold blue]Fetching transcript for:[/bold blue] {url}")
    console.print(f"Language: {lang}, Force: {force}")
    console.print("[yellow]Not implemented yet[/yellow]")


@app.command()
def summarize(
    url: str = typer.Argument(..., help="YouTube URL or video ID to summarize"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-processing even if cached"),
) -> None:
    """Generate summary for a YouTube video."""
    console.print(f"[bold blue]Summarizing:[/bold blue] {url}")
    console.print("[yellow]Not implemented yet[/yellow]")


@app.command()
def ideas(
    url: str = typer.Argument(..., help="YouTube URL or video ID to extract ideas from"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-processing even if cached"),
) -> None:
    """Extract main ideas from a YouTube video."""
    console.print(f"[bold blue]Extracting ideas from:[/bold blue] {url}")
    console.print("[yellow]Not implemented yet[/yellow]")


@app.command()
def takeaways(
    url: str = typer.Argument(..., help="YouTube URL or video ID to extract takeaways from"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-processing even if cached"),
) -> None:
    """Extract takeaways from a YouTube video."""
    console.print(f"[bold blue]Extracting takeaways from:[/bold blue] {url}")
    console.print("[yellow]Not implemented yet[/yellow]")


@app.command()
def process(
    url: str = typer.Argument(..., help="YouTube URL to process completely"),
    lang: str = typer.Option("en", "--lang", "-l", help="Preferred transcript language"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-processing even if cached"),
    outdir: str = typer.Option(None, "--outdir", "-o", help="Output directory (overrides config)"),
) -> None:
    """Process a YouTube video completely (fetch + summarize + ideas + takeaways)."""
    console.print(f"[bold blue]Processing:[/bold blue] {url}")
    console.print(f"Language: {lang}, Force: {force}")
    console.print("[yellow]Not implemented yet[/yellow]")


@app.command()
def config(show: bool = typer.Option(False, "--show", help="Show current configuration")) -> None:
    """Show or manage configuration."""
    if show:
        console.print("[bold blue]Current Configuration:[/bold blue]")
        console.print(f"Output Directory: {settings.output_dir}")
        console.print(f"Cache Enabled: {settings.cache_enabled}")
        console.print(f"Log Level: {settings.log_level}")
        console.print(f"Gemini Model: {settings.gemini_model}")
        if settings.get_proxies():
            console.print(f"Proxies: {settings.get_proxies()}")
    else:
        console.print("Use --show to display current configuration")


if __name__ == "__main__":
    app()
