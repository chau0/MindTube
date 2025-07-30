# TASK-008: Analysis Models

## Task Information
- **ID**: TASK-008
- **Phase**: 1 - Data Models
- **Estimate**: 45 minutes
- **Dependencies**: TASK-007
- **Status**: ✅ Completed

## Description
Implement Summary, KeyIdeas, and Mindmap dataclasses for storing AI analysis results. These models represent the processed output from LLM analysis of video content.

## Acceptance Criteria
- [x] Create Summary dataclass with structured content
- [x] Create KeyIdeas dataclass with categorized insights
- [x] Create Mindmap dataclass with Mermaid format support
- [x] Add JSON serialization/deserialization
- [x] Implement field validation
- [x] Create unit tests
- [x] Add docstrings and type hints
- [x] Support multiple output formats

## Implementation

### Step 1: Create mindtube/models/analysis.py

```python
"""Analysis result models for processed video content."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class SummaryType(str, Enum):
    """Types of summaries that can be generated."""
    BRIEF = "brief"
    DETAILED = "detailed"
    BULLET_POINTS = "bullet_points"
    EXECUTIVE = "executive"


class KeyIdeaCategory(str, Enum):
    """Categories for key ideas."""
    MAIN_CONCEPT = "main_concept"
    ACTIONABLE = "actionable"
    INSIGHT = "insight"
    EXAMPLE = "example"
    DEFINITION = "definition"
    QUOTE = "quote"


class Summary(BaseModel):
    """Summary of video content."""
    
    video_id: str = Field(..., description="YouTube video ID")
    summary_type: SummaryType = Field(SummaryType.BRIEF, description="Type of summary")
    content: str = Field(..., description="Summary content", min_length=10)
    word_count: int = Field(..., description="Word count of summary", gt=0)
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    model_used: str = Field(..., description="AI model used for generation")
    confidence_score: Optional[float] = Field(None, description="Confidence score", ge=0, le=1)
    
    @validator('word_count', pre=True, always=True)
    def calculate_word_count(cls, v, values):
        """Calculate word count from content if not provided."""
        if v is None and 'content' in values:
            return len(values['content'].split())
        return v
    
    def to_markdown(self) -> str:
        """Export summary as Markdown."""
        return f"# Summary\n\n{self.content}\n\n*Generated on {self.generated_at.isoformat()} using {self.model_used}*"
    
    def to_html(self) -> str:
        """Export summary as HTML."""
        return f"""
        <div class="summary">
            <h2>Summary</h2>
            <p>{self.content}</p>
            <small>Generated on {self.generated_at.isoformat()} using {self.model_used}</small>
        </div>
        """


class KeyIdea(BaseModel):
    """A single key idea extracted from video content."""
    
    title: str = Field(..., description="Title of the key idea", min_length=1)
    description: str = Field(..., description="Detailed description", min_length=1)
    category: KeyIdeaCategory = Field(..., description="Category of the idea")
    timestamp: Optional[float] = Field(None, description="Timestamp in video where idea appears", ge=0)
    importance_score: float = Field(..., description="Importance score", ge=0, le=1)
    
    def to_markdown(self) -> str:
        """Export key idea as Markdown."""
        timestamp_str = f" (at {self.timestamp}s)" if self.timestamp else ""
        return f"## {self.title}{timestamp_str}\n\n{self.description}\n\n*Category: {self.category.value}, Importance: {self.importance_score:.2f}*"


class KeyIdeas(BaseModel):
    """Collection of key ideas extracted from video content."""
    
    video_id: str = Field(..., description="YouTube video ID")
    ideas: List[KeyIdea] = Field(..., description="List of key ideas")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    model_used: str = Field(..., description="AI model used for generation")
    
    @validator('ideas')
    def ideas_must_not_be_empty(cls, v):
        """Ensure at least one key idea is present."""
        if not v:
            raise ValueError('Must have at least one key idea')
        return v
    
    def get_by_category(self, category: KeyIdeaCategory) -> List[KeyIdea]:
        """Get ideas filtered by category."""
        return [idea for idea in self.ideas if idea.category == category]
    
    def get_top_ideas(self, limit: int = 5) -> List[KeyIdea]:
        """Get top ideas by importance score."""
        return sorted(self.ideas, key=lambda x: x.importance_score, reverse=True)[:limit]
    
    def to_markdown(self) -> str:
        """Export key ideas as Markdown."""
        content = "# Key Ideas\n\n"
        for idea in self.ideas:
            content += idea.to_markdown() + "\n\n"
        content += f"*Generated on {self.generated_at.isoformat()} using {self.model_used}*"
        return content


class MindmapNode(BaseModel):
    """A node in the mindmap structure."""
    
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node label text", min_length=1)
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    level: int = Field(..., description="Depth level in mindmap", ge=0)
    category: Optional[str] = Field(None, description="Node category")
    
    def to_mermaid_line(self) -> str:
        """Convert node to Mermaid syntax line."""
        if self.parent_id:
            return f"    {self.parent_id} --> {self.id}[{self.label}]"
        else:
            return f"    {self.id}[{self.label}]"


class Mindmap(BaseModel):
    """Mindmap representation of video content."""
    
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Mindmap title", min_length=1)
    nodes: List[MindmapNode] = Field(..., description="Mindmap nodes")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    model_used: str = Field(..., description="AI model used for generation")
    
    @validator('nodes')
    def nodes_must_not_be_empty(cls, v):
        """Ensure at least one node is present."""
        if not v:
            raise ValueError('Mindmap must have at least one node')
        return v
    
    @validator('nodes')
    def validate_node_hierarchy(cls, v):
        """Validate that parent nodes exist."""
        node_ids = {node.id for node in v}
        for node in v:
            if node.parent_id and node.parent_id not in node_ids:
                raise ValueError(f'Parent node {node.parent_id} not found for node {node.id}')
        return v
    
    def get_root_nodes(self) -> List[MindmapNode]:
        """Get nodes without parents (root nodes)."""
        return [node for node in self.nodes if node.parent_id is None]
    
    def get_children(self, parent_id: str) -> List[MindmapNode]:
        """Get child nodes of a specific parent."""
        return [node for node in self.nodes if node.parent_id == parent_id]
    
    def to_mermaid(self) -> str:
        """Export mindmap as Mermaid diagram."""
        lines = ["graph TD"]
        for node in self.nodes:
            lines.append(node.to_mermaid_line())
        return "\n".join(lines)
    
    def to_markdown(self) -> str:
        """Export mindmap as Markdown with Mermaid diagram."""
        content = f"# {self.title}\n\n"
        content += "```mermaid\n"
        content += self.to_mermaid()
        content += "\n```\n\n"
        content += f"*Generated on {self.generated_at.isoformat()} using {self.model_used}*"
        return content
```

### Step 2: Create tests/unit/models/test_analysis.py

```python
"""Tests for analysis models."""

import pytest
from datetime import datetime
from mindtube.models.analysis import (
    Summary, SummaryType, KeyIdea, KeyIdeas, KeyIdeaCategory,
    MindmapNode, Mindmap
)


class TestSummary:
    """Test Summary model."""
    
    def test_valid_summary_creation(self):
        """Test creating a valid summary."""
        summary = Summary(
            video_id="test123",
            summary_type=SummaryType.BRIEF,
            content="This is a test summary with enough words to be valid.",
            word_count=12,
            model_used="gpt-4"
        )
        
        assert summary.video_id == "test123"
        assert summary.summary_type == SummaryType.BRIEF
        assert summary.word_count == 12
        assert summary.model_used == "gpt-4"
    
    def test_word_count_calculation(self):
        """Test automatic word count calculation."""
        summary = Summary(
            video_id="test123",
            content="This has five words exactly.",
            word_count=None,
            model_used="gpt-4"
        )
        
        assert summary.word_count == 5
    
    def test_markdown_export(self):
        """Test Markdown export functionality."""
        summary = Summary(
            video_id="test123",
            content="Test content",
            word_count=2,
            model_used="gpt-4"
        )
        
        markdown = summary.to_markdown()
        assert "# Summary" in markdown
        assert "Test content" in markdown
        assert "gpt-4" in markdown


class TestKeyIdeas:
    """Test KeyIdeas model."""
    
    def test_valid_key_ideas_creation(self):
        """Test creating valid key ideas."""
        ideas = [
            KeyIdea(
                title="Main Concept",
                description="This is the main concept",
                category=KeyIdeaCategory.MAIN_CONCEPT,
                importance_score=0.9
            ),
            KeyIdea(
                title="Action Item",
                description="This is actionable",
                category=KeyIdeaCategory.ACTIONABLE,
                importance_score=0.7
            )
        ]
        
        key_ideas = KeyIdeas(
            video_id="test123",
            ideas=ideas,
            model_used="gpt-4"
        )
        
        assert len(key_ideas.ideas) == 2
        assert key_ideas.video_id == "test123"
    
    def test_get_by_category(self):
        """Test filtering ideas by category."""
        ideas = [
            KeyIdea(
                title="Concept",
                description="A concept",
                category=KeyIdeaCategory.MAIN_CONCEPT,
                importance_score=0.9
            ),
            KeyIdea(
                title="Action",
                description="An action",
                category=KeyIdeaCategory.ACTIONABLE,
                importance_score=0.7
            )
        ]
        
        key_ideas = KeyIdeas(video_id="test", ideas=ideas, model_used="gpt-4")
        main_concepts = key_ideas.get_by_category(KeyIdeaCategory.MAIN_CONCEPT)
        
        assert len(main_concepts) == 1
        assert main_concepts[0].title == "Concept"
    
    def test_get_top_ideas(self):
        """Test getting top ideas by importance."""
        ideas = [
            KeyIdea(
                title="Low",
                description="Low importance",
                category=KeyIdeaCategory.INSIGHT,
                importance_score=0.3
            ),
            KeyIdea(
                title="High",
                description="High importance",
                category=KeyIdeaCategory.MAIN_CONCEPT,
                importance_score=0.9
            )
        ]
        
        key_ideas = KeyIdeas(video_id="test", ideas=ideas, model_used="gpt-4")
        top_ideas = key_ideas.get_top_ideas(1)
        
        assert len(top_ideas) == 1
        assert top_ideas[0].title == "High"


class TestMindmap:
    """Test Mindmap model."""
    
    def test_valid_mindmap_creation(self):
        """Test creating a valid mindmap."""
        nodes = [
            MindmapNode(id="root", label="Main Topic", level=0),
            MindmapNode(id="child1", label="Subtopic 1", parent_id="root", level=1),
            MindmapNode(id="child2", label="Subtopic 2", parent_id="root", level=1)
        ]
        
        mindmap = Mindmap(
            video_id="test123",
            title="Test Mindmap",
            nodes=nodes,
            model_used="gpt-4"
        )
        
        assert mindmap.title == "Test Mindmap"
        assert len(mindmap.nodes) == 3
    
    def test_node_hierarchy_validation(self):
        """Test that parent nodes must exist."""
        nodes = [
            MindmapNode(id="child", label="Child", parent_id="nonexistent", level=1)
        ]
        
        with pytest.raises(ValueError, match="Parent node nonexistent not found"):
            Mindmap(
                video_id="test",
                title="Invalid",
                nodes=nodes,
                model_used="gpt-4"
            )
    
    def test_mermaid_export(self):
        """Test Mermaid diagram export."""
        nodes = [
            MindmapNode(id="root", label="Main", level=0),
            MindmapNode(id="child", label="Sub", parent_id="root", level=1)
        ]
        
        mindmap = Mindmap(
            video_id="test",
            title="Test",
            nodes=nodes,
            model_used="gpt-4"
        )
        
        mermaid = mindmap.to_mermaid()
        assert "graph TD" in mermaid
        assert "root[Main]" in mermaid
        assert "root --> child[Sub]" in mermaid
```

## Implementation Steps

1. **Create analysis models file**
   - Implement Summary with multiple types
   - Implement KeyIdeas with categorization
   - Implement Mindmap with hierarchical structure

2. **Add validation logic**
   - Ensure content quality constraints
   - Validate hierarchical relationships in mindmaps
   - Add importance scoring validation

3. **Create export functionality**
   - Markdown export for all models
   - Mermaid diagram generation for mindmaps
   - HTML export for summaries

4. **Create comprehensive tests**
   - Test model creation and validation
   - Test export functionality
   - Test filtering and sorting methods

## Notes

- Consider adding support for different mindmap layouts
- Export functions should handle special characters properly
- Importance scores help prioritize content
- Timestamps link ideas back to video content

## Potential Issues

**Issue**: Large mindmaps with complex hierarchies
**Solution**: Add depth limits and validation for circular references

**Issue**: Special characters in Mermaid export
**Solution**: Implement proper escaping for node labels