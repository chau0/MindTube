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