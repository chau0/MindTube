# TASK-021: Analyze Command

## Task Information
- **ID**: TASK-021
- **Phase**: 4 - CLI Interface
- **Estimate**: 75 minutes
- **Dependencies**: TASK-020, TASK-019
- **Status**: 🔴 Backlog

## Description
Implement the main analyze CLI command that provides comprehensive video analysis including transcript, summary, key ideas, and mindmap generation.

## Acceptance Criteria
- [ ] Create analyze command with all options
- [ ] Integrate with MindTubeEngine
- [ ] Support all output formats
- [ ] Implement file saving
- [ ] Add progress reporting
- [ ] Handle interruption gracefully
- [ ] Create unit tests
- [ ] Add CLI integration tests

## Implementation Details

### Analyze Command
```python
@app.command()
def analyze(
    video_url: str = typer.Argument(..., help="YouTube video URL to analyze"),
    output_format: List[OutputFormat] = typer.Option(
        [OutputFormat.JSON], 
        "--format", "-f", 
        help="Output format(s): json, markdown, html"
    ),
    output_file: Optional[Path] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path (auto-generated if not specified)"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, 
        "--output-dir", "-d", 
        help="Output directory"
    ),
    language: str = typer.Option(
        "en", 
        "--language", "-l", 
        help="Preferred transcript language"
    ),
    no_summary: bool = typer.Option(
        False, 
        "--no-summary", 
        help="Skip summary generation"
    ),
    no_ideas: bool = typer.Option(
        False, 
        "--no-ideas", 
        help="Skip key ideas extraction"
    ),
    no_mindmap: bool = typer.Option(
        False, 
        "--no-mindmap", 
        help="Skip mindmap generation"
    ),
    save_transcript: bool = typer.Option(
        False, 
        "--save-transcript", 
        help="Save raw transcript"
    ),
):
    """Analyze a YouTube video and extract insights"""
    pass
```

### Progress Reporting Integration
```python
def create_progress_callback(cli_utils: CLIUtils) -> Callable[[str, float], None]:
    """Create progress callback for CLI"""
    progress = CLIProgress(cli_utils.console)
    
    def callback(stage: str, completed: float):
        if completed == 0:
            progress.start_spinner(stage)
        else:
            progress.update_progress(stage, completed)
            if completed >= 1.0:
                progress.stop()
                cli_utils.print_success(f"Completed: {stage}")
    
    return callback
```

### Output File Management
```python
def determine_output_paths(
    video_id: str,
    output_file: Optional[Path],
    output_dir: Optional[Path],
    formats: List[OutputFormat]
) -> Dict[OutputFormat, Path]:
    """Determine output file paths for each format"""
    
    if output_file and len(formats) == 1:
        return {formats[0]: output_file}
    
    base_dir = output_dir or Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    paths = {}
    for fmt in formats:
        filename = f"{video_id}_analysis_{timestamp}.{fmt.value}"
        paths[fmt] = base_dir / filename
    
    return paths
```

### Command Implementation
```python
async def run_analyze_command(
    video_url: str,
    options: AnalysisOptions,
    cli_utils: CLIUtils
) -> None:
    """Main analyze command implementation"""
    
    try:
        # Initialize engine
        config = load_cli_config()
        engine = MindTubeEngine(config)
        
        # Setup progress tracking
        progress_callback = create_progress_callback(cli_utils)
        
        cli_utils.print_info(f"Analyzing video: {video_url}")
        
        # Run analysis
        result = await engine.analyze_video(
            video_url, 
            options.to_dict(),
            progress_callback
        )
        
        # Save results
        if options.save_to_file:
            output_paths = determine_output_paths(
                result.video_metadata.video_id,
                options.output_file,
                options.output_directory,
                options.output_formats
            )
            
            for fmt, path in output_paths.items():
                cli_utils.print_info(f"Saving {fmt.value.upper()} to {path}")
                # Save file using storage adapter
        
        # Display summary
        display_analysis_summary(result, cli_utils)
        
    except KeyboardInterrupt:
        cli_utils.print_warning("Analysis interrupted by user")
        raise typer.Exit(1)
    except Exception as e:
        handle_cli_error(e, cli_utils.verbose)
```

### Result Display
```python
def display_analysis_summary(analysis: VideoAnalysis, cli_utils: CLIUtils) -> None:
    """Display analysis results summary"""
    
    table = Table(title="Analysis Results")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    table.add_row("Video Title", "✅", analysis.video_metadata.title)
    table.add_row("Duration", "✅", str(analysis.video_metadata.duration))
    table.add_row("Transcript", "✅", f"{len(analysis.transcript.segments)} segments")
    
    if analysis.summary:
        table.add_row("Summary", "✅", f"{len(analysis.summary.content)} characters")
    
    if analysis.key_ideas:
        table.add_row("Key Ideas", "✅", f"{len(analysis.key_ideas)} ideas")
    
    if analysis.mindmap:
        table.add_row("Mindmap", "✅", "Generated")
    
    cli_utils.console.print(table)
```

### File Structure
```
mindtube/cli/commands/analyze.py
mindtube/cli/commands/__init__.py
tests/unit/cli/commands/test_analyze.py
tests/integration/cli/test_analyze_command.py
```

## Testing Requirements
- Test command option parsing
- Test progress reporting
- Test file output generation
- Test error handling scenarios
- Test interruption handling
- Integration tests with real video URLs
- Test output format validation

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Command help text comprehensive
- [ ] Error handling user-friendly
- [ ] Code follows project standards
- [ ] Documentation updated