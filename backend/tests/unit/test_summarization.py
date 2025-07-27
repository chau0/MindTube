"""
Unit tests for summarization service
Following TDD guide patterns
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.services.summarization import SummarizationService
from app.models.schemas import TranscriptSegment, SummarySection


class TestSummarizationService:
    """Test summarization service functionality."""
    
    def test_chunk_transcript_basic(self, sample_transcript_segments):
        """Test basic transcript chunking."""
        service = SummarizationService()
        
        chunks = service.chunk_transcript(sample_transcript_segments)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        
        # Verify chunks contain transcript content
        combined_chunks = " ".join(chunks)
        for segment in sample_transcript_segments:
            assert segment.text in combined_chunks
    
    def test_chunk_transcript_empty(self):
        """Test chunking with empty transcript."""
        service = SummarizationService()
        
        chunks = service.chunk_transcript([])
        
        assert chunks == []
    
    def test_chunk_transcript_single_segment(self):
        """Test chunking with single segment."""
        service = SummarizationService()
        
        segments = [TranscriptSegment(
            start_ms=0,
            end_ms=5000,
            text="Single segment text."
        )]
        
        chunks = service.chunk_transcript(segments)
        
        assert len(chunks) == 1
        assert "Single segment text." in chunks[0]
        assert "[00:00]" in chunks[0]  # Should include timestamp
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        service = SummarizationService()
        
        # Test various timestamps
        assert service._format_timestamp(0) == "00:00"
        assert service._format_timestamp(30000) == "00:30"
        assert service._format_timestamp(90000) == "01:30"
        assert service._format_timestamp(3661000) == "61:01"
    
    def test_create_youtube_link(self):
        """Test YouTube link creation with timestamps."""
        service = SummarizationService()
        
        # Test with URL without parameters
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        link = service._create_youtube_link(url, 30000)
        assert link == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        
        # Test with URL with existing parameters
        url_with_params = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=123"
        link = service._create_youtube_link(url_with_params, 45000)
        assert link == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=123&t=45s"
    
    def test_parse_bullet_points(self):
        """Test parsing bullet points from text."""
        service = SummarizationService()
        
        # Test with bullet points
        text_with_bullets = "• First point\n• Second point\n• Third point"
        points = service._parse_bullet_points(text_with_bullets)
        
        assert len(points) == 3
        assert points[0] == "First point"
        assert points[1] == "Second point"
        assert points[2] == "Third point"
        
        # Test with dashes
        text_with_dashes = "- First point\n- Second point"
        points = service._parse_bullet_points(text_with_dashes)
        
        assert len(points) == 2
        assert points[0] == "First point"
        
        # Test with no bullet points (fallback to sentences)
        text_no_bullets = "First sentence. Second sentence. Third sentence."
        points = service._parse_bullet_points(text_no_bullets)
        
        assert len(points) <= 3  # Should limit to 3 points
        assert "First sentence" in points[0]
    
    def test_parse_summary_sections(self, sample_transcript_segments):
        """Test parsing summary sections."""
        service = SummarizationService()
        
        text = "• First key insight\n• Second important point\n• Third takeaway"
        sections = service._parse_summary_sections(text, sample_transcript_segments)
        
        assert len(sections) == 3
        assert all(isinstance(section, SummarySection) for section in sections)
        assert sections[0].content == "First key insight"
        assert sections[1].content == "Second important point"
        assert sections[2].content == "Third takeaway"
        
        # Should have estimated timestamps (some may be None if estimation fails)
        assert len(sections) == 3
        assert all(isinstance(section.timestamp_ms, (int, type(None))) for section in sections)
    
    def test_estimate_timestamp_by_position(self, sample_transcript_segments):
        """Test timestamp estimation by position."""
        service = SummarizationService()
        
        # Test first position
        timestamp = service._estimate_timestamp_by_position(0, 3, sample_transcript_segments)
        assert timestamp == 0
        
        # Test middle position
        timestamp = service._estimate_timestamp_by_position(1, 3, sample_transcript_segments)
        assert timestamp > 0
        assert timestamp < sample_transcript_segments[-1].end_ms
        
        # Test with empty transcript
        timestamp = service._estimate_timestamp_by_position(0, 1, [])
        assert timestamp is None
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_generate_short_summary(self, mock_get_llm_client, sample_transcript_segments):
        """Test short summary generation."""
        # Setup mock
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.generate_summary.return_value = "• Key point 1\n• Key point 2\n• Key point 3"
        
        service = SummarizationService()
        result = await service.generate_short_summary(sample_transcript_segments)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == "Key point 1"
        assert result[1] == "Key point 2"
        assert result[2] == "Key point 3"
        
        # Verify LLM was called
        mock_llm_client.generate_summary.assert_called()
        mock_get_llm_client.assert_called()
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_generate_detailed_summary(self, mock_get_llm_client, sample_transcript_segments):
        """Test detailed summary generation."""
        # Setup mocks
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.process_transcript_chunks.return_value = ["Chunk summary 1", "Chunk summary 2"]
        mock_llm_client.reduce_summaries.return_value = "• Detailed insight 1\n• Detailed insight 2"
        
        service = SummarizationService()
        result = await service.generate_detailed_summary(sample_transcript_segments)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(section, SummarySection) for section in result)
        assert result[0].content == "Detailed insight 1"
        assert result[1].content == "Detailed insight 2"
        
        # Verify LLM methods were called
        mock_llm_client.process_transcript_chunks.assert_called()
        mock_llm_client.reduce_summaries.assert_called()
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_extract_key_ideas(self, mock_get_llm_client, sample_transcript_segments):
        """Test key ideas extraction."""
        # Setup mocks
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.process_transcript_chunks.return_value = ["Ideas chunk 1"]
        mock_llm_client.reduce_summaries.return_value = "• Important concept\n• Key insight"
        
        service = SummarizationService()
        result = await service.extract_key_ideas(sample_transcript_segments)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(section, SummarySection) for section in result)
        
        # Verify correct summary type was used
        mock_llm_client.process_transcript_chunks.assert_called_with(
            service.chunk_transcript(sample_transcript_segments), "key_ideas"
        )
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_extract_actionable_takeaways(self, mock_get_llm_client, sample_transcript_segments):
        """Test actionable takeaways extraction."""
        # Setup mocks
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.process_transcript_chunks.return_value = ["Takeaways chunk 1"]
        mock_llm_client.reduce_summaries.return_value = "• Action step 1\n• Practical advice"
        
        service = SummarizationService()
        result = await service.extract_actionable_takeaways(sample_transcript_segments)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(section, SummarySection) for section in result)
        
        # Verify correct summary type was used
        mock_llm_client.process_transcript_chunks.assert_called_with(
            service.chunk_transcript(sample_transcript_segments), "takeaways"
        )
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_process_complete_video(self, mock_get_llm_client, sample_transcript_segments, mock_youtube_url):
        """Test complete video processing."""
        # Setup mocks for all summary types
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.generate_summary.return_value = "• Short summary point"
        mock_llm_client.process_transcript_chunks.return_value = ["Chunk result"]
        mock_llm_client.reduce_summaries.return_value = "• Processed result"
        
        service = SummarizationService()
        result = await service.process_complete_video(sample_transcript_segments, mock_youtube_url)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "short_summary" in result
        assert "detailed_summary" in result
        assert "key_ideas" in result
        assert "actionable_takeaways" in result
        
        # Verify short summary
        assert isinstance(result["short_summary"], list)
        
        # Verify other summaries are SummarySection objects
        for key in ["detailed_summary", "key_ideas", "actionable_takeaways"]:
            assert isinstance(result[key], list)
            if result[key]:  # If not empty
                assert all(isinstance(item, SummarySection) for item in result[key])
        
        # Verify YouTube links were added
        for section_list in [result["detailed_summary"], result["key_ideas"], result["actionable_takeaways"]]:
            for section in section_list:
                if section.timestamp_ms:
                    assert section.youtube_link is not None
                    assert mock_youtube_url in section.youtube_link
    
    @pytest.mark.asyncio
    @patch('app.services.summarization.get_llm_client')
    async def test_error_handling(self, mock_get_llm_client, sample_transcript_segments):
        """Test error handling in summarization service."""
        # Setup mock to raise exception
        mock_llm_client = mock_get_llm_client.return_value
        mock_llm_client.generate_summary.side_effect = Exception("LLM Error")
        
        service = SummarizationService()
        
        with pytest.raises(Exception, match="LLM Error"):
            await service.generate_short_summary(sample_transcript_segments)