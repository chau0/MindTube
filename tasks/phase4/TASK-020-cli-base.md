# TASK-020: CLI Base Framework

## Task Information
- **ID**: TASK-020
- **Phase**: 4 - CLI Interface
- **Estimate**: 60 minutes
- **Dependencies**: TASK-004
- **Status**: 🔴 Backlog

## Description
Set up Typer CLI framework and common utilities that will be shared across all CLI commands. This provides the foundation for the command-line interface.

## Acceptance Criteria
- [ ] Create main CLI app with Typer
- [ ] Implement common options (verbose, quiet, config)
- [ ] Add global error handling
- [ ] Implement progress indicators
- [ ] Add output formatting utilities
- [ ] Create CLI configuration loading
- [ ] Add basic help and version commands
- [ ] Create unit tests for CLI utilities

## Implementation Details

### Main CLI App
```python
import typer
from typing import Optional
from pathlib import Path
from mindtube.core.config import Config
from mindtube.cli.utils import setup_logging, load_config

app = typer.Typer(
    name="mindtube",
    help="YouTube Learning Assistant - Extract knowledge from videos",
    add_completion=False
)

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Disable caching"),
):
    """Global options and setup"""
    pass
```

### Common CLI Utilities
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

class CLIUtils:
    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.console = Console()
        self.verbose = verbose
        self.quiet = quiet
    
    def print_info(self, message: str) -> None:
        """Print informational message"""
        if not self.quiet:
            self.console.print(f"ℹ️  {message}", style="blue")
    
    def print_success(self, message: str) -> None:
        """Print success message"""
        if not self.quiet:
            self.console.print(f"✅ {message}", style="green")
    
    def print_error(self, message: str) -> None:
        """Print error message"""
        self.console.print(f"❌ {message}", style="red")
    
    def print_warning(self, message: str) -> None:
        """Print warning message"""
        if not self.quiet:
            self.console.print(f"⚠️  {message}", style="yellow")
```

### Progress Indicators
```python
class CLIProgress:
    def __init__(self, console: Console):
        self.console = console
        self.progress = None
    
    def start_spinner(self, message: str) -> None:
        """Start a spinner with message"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        self.progress.start()
        self.task = self.progress.add_task(message, total=None)
    
    def update_progress(self, message: str, completed: float) -> None:
        """Update progress bar"""
        if self.progress:
            self.progress.update(self.task, description=message, completed=completed)
```

### Configuration Loading
```python
def load_cli_config(config_file: Optional[Path] = None) -> Config:
    """Load configuration for CLI usage"""
    if config_file:
        return Config.from_file(config_file)
    
    # Try default locations
    default_locations = [
        Path.home() / ".mindtube" / "config.yaml",
        Path.cwd() / "mindtube.yaml",
    ]
    
    for location in default_locations:
        if location.exists():
            return Config.from_file(location)
    
    return Config()  # Use defaults
```

### Global Error Handling
```python
def handle_cli_error(error: Exception, verbose: bool = False) -> None:
    """Handle CLI errors with appropriate formatting"""
    console = Console()
    
    if isinstance(error, MindTubeException):
        console.print(f"❌ {error.message}", style="red")
        if verbose and error.details:
            console.print(f"Details: {error.details}", style="dim")
    else:
        console.print(f"❌ Unexpected error: {str(error)}", style="red")
        if verbose:
            console.print_exception()
    
    raise typer.Exit(1)
```

### Version and Help Commands
```python
@app.command()
def version():
    """Show version information"""
    from mindtube import __version__
    typer.echo(f"MindTube {__version__}")

@app.command()
def info():
    """Show system information"""
    table = Table(title="MindTube System Information")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    # Add system checks
    table.add_row("Python Version", platform.python_version())
    table.add_row("Config File", str(config_file) if config_file else "Not found")
    
    console.print(table)
```

### File Structure
```
mindtube/cli/main.py
mindtube/cli/utils.py
mindtube/cli/progress.py
mindtube/cli/__init__.py
tests/unit/cli/test_main.py
tests/unit/cli/test_utils.py
```

## Testing Requirements
- Test CLI app initialization
- Test common option parsing
- Test progress indicators
- Test error handling and formatting
- Test configuration loading
- Test help and version commands
- Integration tests with real CLI invocation

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] CLI help text comprehensive
- [ ] Error messages user-friendly
- [ ] Code follows project standards
- [ ] Documentation updated