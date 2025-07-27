"""
Video summarization service using Azure OpenAI
"""

import asyncio
from typing import List, Dict, Any, Optional
from app.services.llm_client import get_llm_client
from app.models.schemas import TranscriptSegment, SummarySection
from app.core.logging import logger
from app.core.config import settings


class SummarizationService:
    """Service for processing video transcripts and generating summaries"""
    
    def __init__(self):
        self.chunk_size = settings.DEFAULT_CHUNK_SIZE_TOKENS
    
    def chunk_transcript(self, transcript: List[TranscriptSegment]) -> List[str]:
        """Split transcript into manageable chunks for processing"""
        try:
            chunks = []
            current_chunk = ""
            current_tokens = 0
            
            for segment in transcript:
                segment_text = f"[{self._format_timestamp(segment.start_ms)}] {segment.text}"
                segment_tokens = get_llm_client().count_tokens(segment_text)
                
                # If adding this segment would exceed chunk size, start new chunk
                if current_tokens + segment_tokens > self.chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = segment_text
                    current_tokens = segment_tokens
                else:
                    current_chunk += "\n" + segment_text
                    current_tokens += segment_tokens
            
            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            logger.info(f"Transcript chunked into {len(chunks)} parts", 
                       total_tokens=sum(get_llm_client().count_tokens(chunk) for chunk in chunks))
            
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk transcript: {e}")
            raise
    
    async def generate_short_summary(self, transcript: List[TranscriptSegment]) -> List[str]:
        """Generate a concise bullet-point summary"""
        try:
            chunks = self.chunk_transcript(transcript)
            
            # For short summary, process chunks and then reduce
            if len(chunks) == 1:
                summary = await get_llm_client().generate_summary(chunks[0], "short")
                return self._parse_bullet_points(summary)
            
            # Process chunks in parallel
            chunk_summaries = await get_llm_client().process_transcript_chunks(chunks, "short")
            
            # Reduce to final summary
            final_summary = await get_llm_client().reduce_summaries(chunk_summaries, "short")
            
            return self._parse_bullet_points(final_summary)
            
        except Exception as e:
            logger.error(f"Failed to generate short summary: {e}")
            raise
    
    async def generate_detailed_summary(self, transcript: List[TranscriptSegment]) -> List[SummarySection]:
        """Generate detailed summary with timestamps"""
        try:
            chunks = self.chunk_transcript(transcript)
            
            # Process chunks in parallel
            chunk_summaries = await get_llm_client().process_transcript_chunks(chunks, "detailed")
            
            # Reduce to final summary
            final_summary = await get_llm_client().reduce_summaries(chunk_summaries, "detailed")
            
            # Convert to SummarySection objects with estimated timestamps
            sections = self._parse_summary_sections(final_summary, transcript)
            
            return sections
            
        except Exception as e:
            logger.error(f"Failed to generate detailed summary: {e}")
            raise
    
    async def extract_key_ideas(self, transcript: List[TranscriptSegment]) -> List[SummarySection]:
        """Extract key ideas and concepts"""
        try:
            chunks = self.chunk_transcript(transcript)
            
            # Process chunks in parallel
            chunk_ideas = await get_llm_client().process_transcript_chunks(chunks, "key_ideas")
            
            # Reduce to final key ideas
            final_ideas = await get_llm_client().reduce_summaries(chunk_ideas, "key_ideas")
            
            # Convert to SummarySection objects
            ideas = self._parse_summary_sections(final_ideas, transcript)
            
            return ideas
            
        except Exception as e:
            logger.error(f"Failed to extract key ideas: {e}")
            raise
    
    async def extract_actionable_takeaways(self, transcript: List[TranscriptSegment]) -> List[SummarySection]:
        """Extract actionable takeaways and advice"""
        try:
            chunks = self.chunk_transcript(transcript)
            
            # Process chunks in parallel
            chunk_takeaways = await get_llm_client().process_transcript_chunks(chunks, "takeaways")
            
            # Reduce to final takeaways
            final_takeaways = await get_llm_client().reduce_summaries(chunk_takeaways, "takeaways")
            
            # Convert to SummarySection objects
            takeaways = self._parse_summary_sections(final_takeaways, transcript)
            
            return takeaways
            
        except Exception as e:
            logger.error(f"Failed to extract actionable takeaways: {e}")
            raise
    
    async def process_complete_video(
        self, 
        transcript: List[TranscriptSegment],
        video_url: str
    ) -> Dict[str, Any]:
        """Process complete video transcript to generate all summary types"""
        try:
            logger.info("Starting complete video processing", 
                       transcript_segments=len(transcript))
            
            # Process all summary types in parallel
            tasks = [
                self.generate_short_summary(transcript),
                self.generate_detailed_summary(transcript),
                self.extract_key_ideas(transcript),
                self.extract_actionable_takeaways(transcript)
            ]
            
            results = await asyncio.gather(*tasks)
            
            short_summary, detailed_summary, key_ideas, takeaways = results
            
            # Add YouTube links to sections
            for section in detailed_summary + key_ideas + takeaways:
                if section.timestamp_ms:
                    section.youtube_link = self._create_youtube_link(video_url, section.timestamp_ms)
            
            logger.info("Complete video processing finished successfully")
            
            return {
                "short_summary": short_summary,
                "detailed_summary": detailed_summary,
                "key_ideas": key_ideas,
                "actionable_takeaways": takeaways
            }
            
        except Exception as e:
            logger.error(f"Failed to process complete video: {e}")
            raise
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """Parse bullet points from LLM response"""
        lines = text.strip().split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Remove bullet point markers
                clean_line = line.lstrip('•-* ').strip()
                if clean_line:
                    bullet_points.append(clean_line)
        
        # If no bullet points found, split by sentences
        if not bullet_points:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            bullet_points = sentences[:3]  # Limit to 3 points
        
        return bullet_points
    
    def _parse_summary_sections(self, text: str, transcript: List[TranscriptSegment]) -> List[SummarySection]:
        """Parse summary text into sections with estimated timestamps"""
        lines = text.strip().split('\n')
        sections = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Remove bullet point markers
                content = line.lstrip('•-* ').strip()
                if content:
                    # Estimate timestamp based on content position
                    timestamp_ms = self._estimate_timestamp(content, transcript)
                    sections.append(SummarySection(
                        content=content,
                        timestamp_ms=timestamp_ms
                    ))
        
        # If no bullet points found, treat as paragraphs
        if not sections:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            for i, paragraph in enumerate(paragraphs):
                timestamp_ms = self._estimate_timestamp_by_position(i, len(paragraphs), transcript)
                sections.append(SummarySection(
                    content=paragraph,
                    timestamp_ms=timestamp_ms
                ))
        
        return sections
    
    def _estimate_timestamp(self, content: str, transcript: List[TranscriptSegment]) -> Optional[int]:
        """Estimate timestamp based on content similarity to transcript"""
        # Simple approach: find transcript segment with highest word overlap
        content_words = set(content.lower().split())
        best_match_timestamp = None
        best_score = 0
        
        for segment in transcript:
            segment_words = set(segment.text.lower().split())
            overlap = len(content_words.intersection(segment_words))
            score = overlap / max(len(content_words), 1)
            
            if score > best_score:
                best_score = score
                best_match_timestamp = segment.start_ms
        
        return best_match_timestamp
    
    def _estimate_timestamp_by_position(
        self, 
        position: int, 
        total_sections: int, 
        transcript: List[TranscriptSegment]
    ) -> Optional[int]:
        """Estimate timestamp based on relative position in content"""
        if not transcript:
            return None
        
        # Calculate relative position in transcript
        total_duration = transcript[-1].end_ms if transcript else 0
        estimated_time = (position / max(total_sections, 1)) * total_duration
        
        return int(estimated_time)
    
    def _create_youtube_link(self, video_url: str, timestamp_ms: int) -> str:
        """Create YouTube link with timestamp"""
        seconds = timestamp_ms // 1000
        if '?' in video_url:
            return f"{video_url}&t={seconds}s"
        else:
            return f"{video_url}?t={seconds}s"
    
    def _format_timestamp(self, ms: int) -> str:
        """Format milliseconds as MM:SS"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"


# Global service instance
summarization_service = SummarizationService()