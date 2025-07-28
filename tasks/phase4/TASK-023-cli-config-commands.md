# TASK-023: CLI Configuration Commands

## Task Information
- **ID**: TASK-023
- **Phase**: 4 - CLI Interface
- **Estimate**: 45 minutes
- **Dependencies**: TASK-022
- **Status**: 🔴 Backlog

## Description
Implement configuration management commands for the CLI that allow users to view, set, and validate their MindTube configuration settings.

## Acceptance Criteria
- [ ] Create config show command
- [ ] Create config set command
- [ ] Create config validate command
- [ ] Add config file initialization
- [ ] Implement secure credential handling
- [ ] Create unit tests
- [ ] Add CLI integration tests

## Implementation Details

### Config Command Group
```python
config_app = typer.Typer(help="Configuration management commands")
app.add_typer(config_app, name="config")

@config_app.command("show")
def config_show(
    key: Optional[str] = typer.Argument(None, help="Specific config key to show"),
    show_secrets: bool = typer.Option(False, "--show-secrets", help="Show masked secrets"),
):
    """Show current configuration"""
    pass

@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Set configuration value"""
    pass

@config_app.command("validate")
def config_validate(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Validate configuration"""
    pass

@config_app.command("init")
def config_init(
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing config"),
):
    """Initialize configuration file"""
    pass
```

### Configuration Display
```python
def display_config(config: Config, show_secrets: bool = False, specific_key: Optional[str] = None):
    """Display configuration in a formatted table"""
    
    console = Console()
    
    if specific_key:
        value = getattr(config, specific_key, None)
        if value is None:
            console.print(f"❌ Configuration key '{specific_key}' not found", style="red")
            return
        
        if is_secret_key(specific_key) and not show_secrets:
            value = mask_secret(value)
        
        console.print(f"{specific_key}: {value}")
        return
    
    table = Table(title="MindTube Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Source", style="dim")
    
    config_items = [
        ("azure_openai.endpoint", config.azure_openai.endpoint, "config"),
        ("azure_openai.api_key", mask_secret(config.azure_openai.api_key) if not show_secrets else config.azure_openai.api_key, "config"),
        ("azure_openai.deployment_name", config.azure_openai.deployment_name, "config"),
        ("cache.enabled", str(config.cache.enabled), "config"),
        ("cache.ttl_hours", str(config.cache.ttl_hours), "config"),
        ("output.default_format", config.output.default_format, "config"),
    ]
    
    for key, value, source in config_items:
        table.add_row(key, str(value), source)
    
    console.print(table)

def mask_secret(value: str) -> str:
    """Mask secret values for display"""
    if not value:
        return "Not set"
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}" if len(value) > 8 else "****"

def is_secret_key(key: str) -> bool:
    """Check if a key contains secret information"""
    secret_patterns = ['api_key', 'password', 'token', 'secret']
    return any(pattern in key.lower() for pattern in secret_patterns)
```

### Configuration Setting
```python
def set_config_value(key: str, value: str, config_file: Optional[Path] = None) -> None:
    """Set a configuration value"""
    
    console = Console()
    
    # Determine config file path
    if not config_file:
        config_file = Path.home() / ".mindtube" / "config.yaml"
    
    # Load existing config or create new
    if config_file.exists():
        config = Config.from_file(config_file)
    else:
        config = Config()
        config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Set the value using dot notation
    try:
        set_nested_value(config, key, value)
        
        # Save updated config
        config.save_to_file(config_file)
        
        console.print(f"✅ Set {key} = {value}", style="green")
        console.print(f"Configuration saved to {config_file}", style="dim")
        
    except ValueError as e:
        console.print(f"❌ Invalid configuration: {e}", style="red")
        raise typer.Exit(1)

def set_nested_value(obj: Any, key: str, value: str) -> None:
    """Set nested configuration value using dot notation"""
    keys = key.split('.')
    current = obj
    
    for k in keys[:-1]:
        if not hasattr(current, k):
            raise ValueError(f"Invalid configuration key: {key}")
        current = getattr(current, k)
    
    final_key = keys[-1]
    if not hasattr(current, final_key):
        raise ValueError(f"Invalid configuration key: {key}")
    
    # Convert value to appropriate type
    current_value = getattr(current, final_key)
    if isinstance(current_value, bool):
        value = value.lower() in ('true', '1', 'yes', 'on')
    elif isinstance(current_value, int):
        value = int(value)
    elif isinstance(current_value, float):
        value = float(value)
    
    setattr(current, final_key, value)
```

### Configuration Validation
```python
def validate_config(config_file: Optional[Path] = None) -> None:
    """Validate configuration file"""
    
    console = Console()
    
    if not config_file:
        config_file = Path.home() / ".mindtube" / "config.yaml"
    
    if not config_file.exists():
        console.print(f"❌ Configuration file not found: {config_file}", style="red")
        raise typer.Exit(1)
    
    try:
        config = Config.from_file(config_file)
        
        # Validate configuration
        validation_results = []
        
        # Check Azure OpenAI settings
        if not config.azure_openai.endpoint:
            validation_results.append(("❌", "Azure OpenAI endpoint not configured"))
        else:
            validation_results.append(("✅", "Azure OpenAI endpoint configured"))
        
        if not config.azure_openai.api_key:
            validation_results.append(("❌", "Azure OpenAI API key not configured"))
        else:
            validation_results.append(("✅", "Azure OpenAI API key configured"))
        
        # Test connectivity (optional)
        if config.azure_openai.endpoint and config.azure_openai.api_key:
            try:
                # Test connection
                validation_results.append(("✅", "Azure OpenAI connection successful"))
            except Exception as e:
                validation_results.append(("❌", f"Azure OpenAI connection failed: {e}"))
        
        # Display results
        table = Table(title="Configuration Validation")
        table.add_column("Status", style="bold")
        table.add_column("Check")
        
        for status, message in validation_results:
            table.add_row(status, message)
        
        console.print(table)
        
        # Exit with error if any checks failed
        if any(result[0] == "❌" for result in validation_results):
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"❌ Configuration validation failed: {e}", style="red")
        raise typer.Exit(1)
```

### Configuration Initialization
```python
def init_config(config_file: Optional[Path] = None, force: bool = False) -> None:
    """Initialize configuration file with defaults"""
    
    console = Console()
    
    if not config_file:
        config_file = Path.home() / ".mindtube" / "config.yaml"
    
    if config_file.exists() and not force:
        console.print(f"❌ Configuration file already exists: {config_file}", style="red")
        console.print("Use --force to overwrite", style="dim")
        raise typer.Exit(1)
    
    # Create directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create default configuration
    config = Config()
    
    # Interactive setup for required fields
    console.print("🚀 Setting up MindTube configuration", style="bold blue")
    
    endpoint = typer.prompt("Azure OpenAI Endpoint URL")
    api_key = typer.prompt("Azure OpenAI API Key", hide_input=True)
    deployment = typer.prompt("Azure OpenAI Deployment Name", default="gpt-4")
    
    config.azure_openai.endpoint = endpoint
    config.azure_openai.api_key = api_key
    config.azure_openai.deployment_name = deployment
    
    # Save configuration
    config.save_to_file(config_file)
    
    console.print(f"✅ Configuration saved to {config_file}", style="green")
    console.print("Run 'mindtube config validate' to test your settings", style="dim")
```

### File Structure
```
mindtube/cli/commands/config.py
tests/unit/cli/commands/test_config.py
tests/integration/cli/test_config_commands.py
```

## Testing Requirements
- Test config show with and without secrets
- Test config set with various value types
- Test config validation scenarios
- Test config initialization
- Test error handling for invalid keys/values
- Integration tests with real config files

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Secure credential handling verified
- [ ] Command help text comprehensive
- [ ] Code follows project standards
- [ ] Documentation updated