# TASK-022: Individual Commands

## Task Information
- **ID**: TASK-022
- **Phase**: 4 - CLI Interface
- **Estimate**: 90 minutes
- **Dependencies**: TASK-021
- **Status**: 🔴 Backlog

## Description
Implement individual CLI commands for transcript, summarize, and mindmap operations. These commands provide focused functionality for users who need specific outputs.

## Acceptance Criteria
- [ ] Create transcript command
- [ ] Create summarize command
- [ ] Create mindmap command
- [ ] Share common functionality with analyze
- [ ] Support command-specific options
- [ ] Add proper error handling
- [ ] Create unit tests for each command
- [ ] Add CLI integration tests

## Implementation Details

### Transcript Command
```python
@app.command()
def transcript(
    video_url: str = typer.Argument(..., help="YouTube video URL"),
    language: str = typer.Option("en", "--language", "-l", help="Preferred language"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: OutputFormat = typer.Option(OutputFormat.JSON, "--format", "-f", help="Output format"),
    include_timestamps: bool = typer.Option(True, "--timestamps/--no-timestamps", help="Include timestamps"),
):
    """Extract transcript from YouTube video"""
    pass
```

### Summarize Command
```python
@app.command()
def summarize(
    video_url: str = typer.Argument(..., help="YouTube video URL"),
    length: SummaryLength = typer.Option(SummaryLength.MEDIUM, "--length", help="Summary length"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, "--format", "-f", help="Output format"),
    include_transcript: bool = typer.Option(False, "--include-transcript", help="Include original transcript"),
):
    """Generate summary of YouTube video"""
    pass
```

### Mindmap Command
```python
@app.command()
def mindmap(
    video_url: str = typer.Argument(..., help="YouTube video URL"),
    style: MindmapStyle = typer.Option(MindmapStyle.HIERARCHICAL, "--style", help="Mindmap style"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: OutputFormat = typer.Option(OutputFormat.MARKDOWN, "--format", "-f", help="Output format"),
    max_depth: int = typer.Option(3, "--max-depth", help="Maximum hierarchy depth"),
):
    """Generate mindmap from YouTube video"""
    pass
```

### Shared Command Base
```python
from abc import ABC, abstractmethod

class BaseCommand(ABC):
    def __init__(self, cli_utils: CLIUtils, config: Config):
        self.cli_utils = cli_utils
        self.config = config
        self.engine = MindTubeEngine(config)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the command"""
        pass
    
    def setup_progress_callback(self) -> Callable[[str, float], None]:
        """Setup progress tracking"""
        return create_progress_callback(self.cli_utils)
    
    def save_result(self, result: Any, output_file: Optional[Path], format: OutputFormat) -> None:
        """Save result to file"""
        if output_file:
            # Save using storage adapter
            self.cli_utils.print_success(f"Saved to {output_file}")
        else:
            # Print to stdout
            self.display_result(result, format)
```

### Command Implementations
```python
class TranscriptCommand(BaseCommand):
    async def execute(
        self, 
        video_url: str, 
        language: str, 
        include_timestamps: bool,
        **kwargs
    ) -> Transcript:
        """Execute transcript extraction"""
        
        progress_callback = self.setup_progress_callback()
        self.cli_utils.print_info(f"Extracting transcript from: {video_url}")
        
        transcript = await self.engine.get_transcript_only(video_url)
        
        if not include_timestamps:
            # Remove timestamp information
            transcript = self.strip_timestamps(transcript)
        
        return transcript
    
    def strip_timestamps(self, transcript: Transcript) -> Transcript:
        """Remove timestamp information from transcript"""
        # Implementation to create text-only version
        pass

class SummaryCommand(BaseCommand):
    async def execute(
        self, 
        video_url: str, 
        length: SummaryLength,
        include_transcript: bool,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute summary generation"""
        
        progress_callback = self.setup_progress_callback()
        self.cli_utils.print_info(f"Generating summary for: {video_url}")
        
        # Get transcript first
        transcript = await self.engine.get_transcript_only(video_url)
        
        # Generate summary with specific length
        analysis_options = AnalysisOptions(
            include_summary=True,
            include_key_ideas=False,
            include_mindmap=False,
            summary_length=length
        )
        
        analysis = await self.engine.analyze_transcript(transcript)
        
        result = {
            'summary': analysis.summary,
            'video_metadata': analysis.video_metadata
        }
        
        if include_transcript:
            result['transcript'] = transcript
        
        return result

class MindmapCommand(BaseCommand):
    async def execute(
        self, 
        video_url: str, 
        style: MindmapStyle,
        max_depth: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute mindmap generation"""
        
        progress_callback = self.setup_progress_callback()
        self.cli_utils.print_info(f"Generating mindmap for: {video_url}")
        
        # Get transcript and generate mindmap
        transcript = await self.engine.get_transcript_only(video_url)
        
        analysis_options = AnalysisOptions(
            include_summary=False,
            include_key_ideas=False,
            include_mindmap=True,
            mindmap_style=style,
            mindmap_max_depth=max_depth
        )
        
        analysis = await self.engine.analyze_transcript(transcript)
        
        return {
            'mindmap': analysis.mindmap,
            'video_metadata': analysis.video_metadata
        }
```

### Command Registration
```python
# Register commands with the main app
def register_commands():
    """Register all individual commands"""
    
    @app.command()
    def transcript_cmd(
        ctx: typer.Context,
        video_url: str = typer.Argument(...),
        language: str = typer.Option("en", "--language", "-l"),
        output_file: Optional[Path] = typer.Option(None, "--output", "-o"),
        format: OutputFormat = typer.Option(OutputFormat.JSON, "--format", "-f"),
        include_timestamps: bool = typer.Option(True, "--timestamps/--no-timestamps"),
    ):
        """Extract transcript from YouTube video"""
        cli_utils = CLIUtils(ctx.obj.get('verbose', False), ctx.obj.get('quiet', False))
        config = ctx.obj['config']
        
        command = TranscriptCommand(cli_utils, config)
        
        try:
            result = asyncio.run(command.execute(
                video_url=video_url,
                language=language,
                include_timestamps=include_timestamps
            ))
            command.save_result(result, output_file, format)
        except Exception as e:
            handle_cli_error(e, cli_utils.verbose)
```

### File Structure
```
mindtube/cli/commands/transcript.py
mindtube/cli/commands/summarize.py
mindtube/cli/commands/mindmap.py
mindtube/cli/commands/base.py
tests/unit/cli/commands/test_transcript.py
tests/unit/cli/commands/test_summarize.py
tests/unit/cli/commands/test_mindmap.py
tests/integration/cli/test_individual_commands.py
```

## Testing Requirements
- Test each command independently
- Test command-specific options
- Test output format handling
- Test file saving functionality
- Test error scenarios for each command
- Integration tests with real YouTube videos
- Test command help and usage

## Definition of Done
- [ ] All acceptance criteria completed
- [ ] Unit tests written and passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Command help text comprehensive
- [ ] Error handling user-friendly
- [ ] Code follows project standards
- [ ] Documentation updated