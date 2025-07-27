"""
Azure OpenAI LLM Client Service
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI, AsyncAzureOpenAI
from app.core.config import settings
from app.core.logging import logger
import tiktoken


class AzureOpenAIClient:
    """Azure OpenAI client wrapper with cost tracking and error handling"""
    
    def __init__(self):
        self.client = None
        self.async_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize Azure OpenAI clients"""
        try:
            # Get Azure OpenAI configuration from environment
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            
            if not azure_endpoint or not api_key:
                raise ValueError("Azure OpenAI endpoint and API key must be provided")
            
            # Initialize synchronous client
            self.client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            
            # Initialize asynchronous client
            self.async_client = AsyncAzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            
            logger.info("Azure OpenAI clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI clients: {e}")
            raise
    
    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text using tiktoken"""
        try:
            # Map Azure deployment names to OpenAI model names for tiktoken
            model_mapping = {
                "gpt-35-turbo": "gpt-3.5-turbo",
                "gpt-4": "gpt-4",
                "gpt-4-32k": "gpt-4-32k",
                "gpt-4o": "gpt-4o",
                "gpt-4o-mini": "gpt-4o-mini"
            }
            
            tiktoken_model = model_mapping.get(model, "gpt-4")
            encoding = tiktoken.encoding_for_model(tiktoken_model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Failed to count tokens, using estimate: {e}")
            # Fallback: rough estimate of 4 characters per token
            return len(text) // 4
    
    async def generate_summary(
        self,
        text: str,
        summary_type: str = "detailed",
        model: Optional[str] = None
    ) -> str:
        """Generate summary using Azure OpenAI"""
        try:
            # Use configured model or default
            deployment_name = model or settings.DEFAULT_MAP_MODEL
            
            # Create appropriate prompt based on summary type
            prompts = {
                "short": "Provide a concise 2-3 bullet point summary of the key points from this transcript:",
                "detailed": "Provide a detailed summary with key insights, main topics, and important details from this transcript:",
                "key_ideas": "Extract the 3-5 most important key ideas or concepts from this transcript:",
                "takeaways": "Identify 3-5 actionable takeaways or practical advice from this transcript:"
            }
            
            prompt = prompts.get(summary_type, prompts["detailed"])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at analyzing and summarizing video content. Provide clear, well-structured summaries that capture the essence of the content."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nTranscript:\n{text}"
                }
            ]
            
            # Count tokens for cost tracking
            input_tokens = sum(self.count_tokens(msg["content"], deployment_name) for msg in messages)
            
            logger.info(f"Generating {summary_type} summary", 
                       model=deployment_name, 
                       input_tokens=input_tokens)
            
            # Make API call
            response = await self.async_client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS_PER_REQUEST
            )
            
            # Extract response
            summary = response.choices[0].message.content
            output_tokens = self.count_tokens(summary, deployment_name)
            
            logger.info(f"Summary generated successfully", 
                       summary_type=summary_type,
                       input_tokens=input_tokens,
                       output_tokens=output_tokens,
                       total_tokens=input_tokens + output_tokens)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate {summary_type} summary: {e}")
            raise
    
    async def process_transcript_chunks(
        self,
        chunks: List[str],
        summary_type: str = "detailed"
    ) -> List[str]:
        """Process multiple transcript chunks in parallel"""
        try:
            logger.info(f"Processing {len(chunks)} chunks for {summary_type} summaries")
            
            # Create tasks for parallel processing
            tasks = [
                self.generate_summary(chunk, summary_type)
                for chunk in chunks
            ]
            
            # Execute tasks with concurrency limit
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
            
            async def process_with_semaphore(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[
                process_with_semaphore(task) for task in tasks
            ])
            
            logger.info(f"Successfully processed {len(results)} chunks")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process transcript chunks: {e}")
            raise
    
    async def reduce_summaries(
        self,
        summaries: List[str],
        summary_type: str = "detailed"
    ) -> str:
        """Combine multiple summaries into a final coherent summary"""
        try:
            if len(summaries) == 1:
                return summaries[0]
            
            combined_text = "\n\n".join(f"Section {i+1}:\n{summary}" 
                                      for i, summary in enumerate(summaries))
            
            reduction_prompts = {
                "short": "Combine these section summaries into a concise 2-3 bullet point overall summary:",
                "detailed": "Combine these section summaries into a comprehensive, well-structured summary that flows naturally:",
                "key_ideas": "Synthesize these sections to identify the most important key ideas or concepts:",
                "takeaways": "Combine these sections to create a cohesive list of actionable takeaways:"
            }
            
            prompt = reduction_prompts.get(summary_type, reduction_prompts["detailed"])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at synthesizing information. Combine the provided summaries into a coherent, well-structured final summary without redundancy."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{combined_text}"
                }
            ]
            
            model = settings.DEFAULT_REDUCE_MODEL
            input_tokens = sum(self.count_tokens(msg["content"], model) for msg in messages)
            
            logger.info(f"Reducing {len(summaries)} summaries", 
                       model=model, 
                       input_tokens=input_tokens)
            
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS_PER_REQUEST
            )
            
            final_summary = response.choices[0].message.content
            output_tokens = self.count_tokens(final_summary, model)
            
            logger.info(f"Summary reduction completed", 
                       input_tokens=input_tokens,
                       output_tokens=output_tokens)
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Failed to reduce summaries: {e}")
            raise


# Global client instance
llm_client = AzureOpenAIClient()