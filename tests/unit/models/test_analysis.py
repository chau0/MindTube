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

    def test_html_export(self):
        """Test HTML export functionality."""
        summary = Summary(
            video_id="test123",
            content="Test content",
            word_count=2,
            model_used="gpt-4"
        )
        
        html = summary.to_html()
        assert "<div class=\"summary\">" in html
        assert "<h2>Summary</h2>" in html
        assert "Test content" in html
        assert "gpt-4" in html

    def test_content_validation(self):
        """Test content length validation."""
        with pytest.raises(ValueError, match="at least 10 characters"):
            Summary(
                video_id="test123",
                content="short",
                word_count=1,
                model_used="gpt-4"
            )


class TestKeyIdea:
    """Test KeyIdea model."""
    
    def test_valid_key_idea_creation(self):
        """Test creating a valid key idea."""
        idea = KeyIdea(
            title="Main Concept",
            description="This is the main concept",
            category=KeyIdeaCategory.MAIN_CONCEPT,
            importance_score=0.9,
            timestamp=120.5
        )
        
        assert idea.title == "Main Concept"
        assert idea.category == KeyIdeaCategory.MAIN_CONCEPT
        assert idea.importance_score == 0.9
        assert idea.timestamp == 120.5
    
    def test_markdown_export(self):
        """Test key idea Markdown export."""
        idea = KeyIdea(
            title="Test Idea",
            description="Test description",
            category=KeyIdeaCategory.ACTIONABLE,
            importance_score=0.8,
            timestamp=60.0
        )
        
        markdown = idea.to_markdown()
        assert "## Test Idea (at 60.0s)" in markdown
        assert "Test description" in markdown
        assert "Category: actionable" in markdown
        assert "Importance: 0.80" in markdown
    
    def test_markdown_export_without_timestamp(self):
        """Test key idea Markdown export without timestamp."""
        idea = KeyIdea(
            title="Test Idea",
            description="Test description",
            category=KeyIdeaCategory.INSIGHT,
            importance_score=0.7
        )
        
        markdown = idea.to_markdown()
        assert "## Test Idea\n\n" in markdown
        assert "(at " not in markdown


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
    
    def test_empty_ideas_validation(self):
        """Test that empty ideas list is not allowed."""
        with pytest.raises(ValueError, match="Must have at least one key idea"):
            KeyIdeas(
                video_id="test123",
                ideas=[],
                model_used="gpt-4"
            )
    
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
            ),
            KeyIdea(
                title="Medium",
                description="Medium importance",
                category=KeyIdeaCategory.ACTIONABLE,
                importance_score=0.6
            )
        ]
        
        key_ideas = KeyIdeas(video_id="test", ideas=ideas, model_used="gpt-4")
        top_ideas = key_ideas.get_top_ideas(2)
        
        assert len(top_ideas) == 2
        assert top_ideas[0].title == "High"
        assert top_ideas[1].title == "Medium"
    
    def test_markdown_export(self):
        """Test key ideas Markdown export."""
        ideas = [
            KeyIdea(
                title="Test Idea",
                description="Test description",
                category=KeyIdeaCategory.MAIN_CONCEPT,
                importance_score=0.8
            )
        ]
        
        key_ideas = KeyIdeas(video_id="test", ideas=ideas, model_used="gpt-4")
        markdown = key_ideas.to_markdown()
        
        assert "# Key Ideas" in markdown
        assert "## Test Idea" in markdown
        assert "gpt-4" in markdown


class TestMindmapNode:
    """Test MindmapNode model."""
    
    def test_valid_node_creation(self):
        """Test creating a valid mindmap node."""
        node = MindmapNode(
            id="node1",
            label="Test Node",
            parent_id="parent1",
            level=1,
            category="concept"
        )
        
        assert node.id == "node1"
        assert node.label == "Test Node"
        assert node.parent_id == "parent1"
        assert node.level == 1
        assert node.category == "concept"
    
    def test_mermaid_line_with_parent(self):
        """Test Mermaid line generation with parent."""
        node = MindmapNode(
            id="child",
            label="Child Node",
            parent_id="parent",
            level=1
        )
        
        line = node.to_mermaid_line()
        assert line == "    parent --> child[Child Node]"
    
    def test_mermaid_line_without_parent(self):
        """Test Mermaid line generation without parent."""
        node = MindmapNode(
            id="root",
            label="Root Node",
            level=0
        )
        
        line = node.to_mermaid_line()
        assert line == "    root[Root Node]"


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
        assert mindmap.video_id == "test123"
    
    def test_empty_nodes_validation(self):
        """Test that empty nodes list is not allowed."""
        with pytest.raises(ValueError, match="Mindmap must have at least one node"):
            Mindmap(
                video_id="test123",
                title="Empty Mindmap",
                nodes=[],
                model_used="gpt-4"
            )
    
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
    
    def test_get_root_nodes(self):
        """Test getting root nodes."""
        nodes = [
            MindmapNode(id="root1", label="Root 1", level=0),
            MindmapNode(id="root2", label="Root 2", level=0),
            MindmapNode(id="child", label="Child", parent_id="root1", level=1)
        ]
        
        mindmap = Mindmap(
            video_id="test",
            title="Test",
            nodes=nodes,
            model_used="gpt-4"
        )
        
        root_nodes = mindmap.get_root_nodes()
        assert len(root_nodes) == 2
        assert {node.id for node in root_nodes} == {"root1", "root2"}
    
    def test_get_children(self):
        """Test getting child nodes."""
        nodes = [
            MindmapNode(id="root", label="Root", level=0),
            MindmapNode(id="different", label="Different Root", level=0),
            MindmapNode(id="child1", label="Child 1", parent_id="root", level=1),
            MindmapNode(id="child2", label="Child 2", parent_id="root", level=1),
            MindmapNode(id="other", label="Other", parent_id="different", level=1)
        ]
        
        mindmap = Mindmap(
            video_id="test",
            title="Test",
            nodes=nodes,
            model_used="gpt-4"
        )
        
        children = mindmap.get_children("root")
        assert len(children) == 2
        assert {child.id for child in children} == {"child1", "child2"}
    
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
    
    def test_markdown_export(self):
        """Test Markdown export with Mermaid diagram."""
        nodes = [
            MindmapNode(id="root", label="Main", level=0)
        ]
        
        mindmap = Mindmap(
            video_id="test",
            title="Test Mindmap",
            nodes=nodes,
            model_used="gpt-4"
        )
        
        markdown = mindmap.to_markdown()
        assert "# Test Mindmap" in markdown
        assert "```mermaid" in markdown
        assert "graph TD" in markdown
        assert "gpt-4" in markdown