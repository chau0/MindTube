"""
Unit tests for Azure OpenAI LLM client
Following TDD guide patterns
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from app.services.llm_client import AzureOpenAIClient


class TestAzureOpenAIClient:
    """Test Azure OpenAI client functionality."""
    
    def test_token_counting(self):
        """Test token counting functionality."""
        client = AzureOpenAIClient()
        
        # Test basic token counting
        text = "This is a test sentence."
        tokens = client.count_tokens(text)
        
        assert isinstance(tokens, int)
        assert tokens > 0
        assert tokens < 100  # Should be reasonable for short text
    
    def test_token_counting_empty_text(self):
        """Test token counting with empty text."""
        client = AzureOpenAIClient()
        
        tokens = client.count_tokens("")
        assert tokens == 0
    
    def test_token_counting_different_models(self):
        """Test token counting with different model names."""
        client = AzureOpenAIClient()
        
        text = "Test text for token counting."
        
        # Test with different model mappings
        tokens_gpt4 = client.count_tokens(text, "gpt-4")
        tokens_gpt35 = client.count_tokens(text, "gpt-35-turbo")
        
        assert isinstance(tokens_gpt4, int)
        assert isinstance(tokens_gpt35, int)
        # Tokens should be similar for same text
        assert abs(tokens_gpt4 - tokens_gpt35) <= 2
    
    @patch('app.services.llm_client.AzureOpenAI')
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    def test_client_initialization_success(self, mock_async_client, mock_sync_client, mock_env_vars):
        """Test successful client initialization."""
        # Mock the clients
        mock_sync_instance = Mock()
        mock_async_instance = Mock()
        mock_sync_client.return_value = mock_sync_instance
        mock_async_client.return_value = mock_async_instance
        
        # Initialize client and trigger initialization
        client = AzureOpenAIClient()
        client._initialize_clients()  # Explicitly call to test initialization
        
        # Verify clients were created
        assert client.client == mock_sync_instance
        assert client.async_client == mock_async_instance
        assert client._initialized == True
        
        # Verify clients were initialized with correct parameters
        mock_sync_client.assert_called_once()
        mock_async_client.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_client_initialization_missing_credentials(self):
        """Test client initialization with missing credentials."""
        client = AzureOpenAIClient()
        # Should raise error when trying to initialize
        with pytest.raises(ValueError, match="Azure OpenAI endpoint and API key must be provided"):
            client._initialize_clients()
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_generate_summary_success(self, mock_async_client, mock_env_vars):
        """Test successful summary generation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test summary."
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_async_client.return_value = mock_client_instance
        
        # Test summary generation
        client = AzureOpenAIClient()
        result = await client.generate_summary("Test transcript text", "short")
        
        assert result == "This is a test summary."
        mock_client_instance.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_generate_summary_different_types(self, mock_async_client, mock_env_vars):
        """Test summary generation with different types."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Generated summary content."
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_async_client.return_value = mock_client_instance
        
        client = AzureOpenAIClient()
        
        # Test different summary types
        summary_types = ["short", "detailed", "key_ideas", "takeaways"]
        
        for summary_type in summary_types:
            result = await client.generate_summary("Test text", summary_type)
            assert result == "Generated summary content."
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_process_transcript_chunks(self, mock_async_client, mock_env_vars):
        """Test processing multiple transcript chunks."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Chunk summary."
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_async_client.return_value = mock_client_instance
        
        client = AzureOpenAIClient()
        
        chunks = ["Chunk 1 text", "Chunk 2 text", "Chunk 3 text"]
        results = await client.process_transcript_chunks(chunks, "detailed")
        
        assert len(results) == 3
        assert all(result == "Chunk summary." for result in results)
        
        # Verify API was called for each chunk
        assert mock_client_instance.chat.completions.create.call_count == 3
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_reduce_summaries_single_summary(self, mock_async_client, mock_env_vars):
        """Test reducing summaries when only one summary exists."""
        mock_async_client.return_value = AsyncMock()
        
        client = AzureOpenAIClient()
        
        summaries = ["Single summary"]
        result = await client.reduce_summaries(summaries, "detailed")
        
        # Should return the single summary without API call
        assert result == "Single summary"
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_reduce_summaries_multiple(self, mock_async_client, mock_env_vars):
        """Test reducing multiple summaries."""
        # Setup mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Combined final summary."
        
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_async_client.return_value = mock_client_instance
        
        client = AzureOpenAIClient()
        
        summaries = ["Summary 1", "Summary 2", "Summary 3"]
        result = await client.reduce_summaries(summaries, "detailed")
        
        assert result == "Combined final summary."
        mock_client_instance.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.llm_client.AsyncAzureOpenAI')
    async def test_api_error_handling(self, mock_async_client, mock_env_vars):
        """Test handling of API errors."""
        # Setup mock to raise exception
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_async_client.return_value = mock_client_instance
        
        client = AzureOpenAIClient()
        
        with pytest.raises(Exception, match="API Error"):
            await client.generate_summary("Test text", "short")