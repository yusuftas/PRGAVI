import os
import re
import logging
from typing import Optional, Dict
from elevenlabs import generate, save, voices, Voice
from elevenlabs.api import History
import anthropic
from config import config

logger = logging.getLogger(__name__)

class AIContentProcessor:
    """AI processor for content generation and voice synthesis"""
    
    def __init__(self):
        self.elevenlabs_api_key = config.ELEVENLABS_API_KEY
        self.anthropic_client = None
        
        # Initialize Anthropic client if API key is available
        if config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        
        # Set ElevenLabs API key
        if self.elevenlabs_api_key:
            os.environ["ELEVENLABS_API_KEY"] = self.elevenlabs_api_key
        
        self.voice_model = config.VOICE_MODEL
        self.available_voices = None
        
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean text"""
        # Remove HTML tags
        clean = re.sub('<.*?>', '', text)
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean
    
    def _get_available_voices(self) -> list:
        """Get list of available ElevenLabs voices"""
        if self.available_voices is None:
            try:
                self.available_voices = voices()
                logger.info(f"Found {len(self.available_voices)} available voices")
            except Exception as e:
                logger.error(f"Error fetching voices: {e}")
                self.available_voices = []
        
        return self.available_voices
    
    def summarize_for_short(self, description: str, max_words: int = 80) -> str:
        """
        Create a short, engaging script from game description
        Optimized for 40-second video format
        """
        if not description:
            return ""
        
        # Clean the description
        clean_desc = self._clean_html(description)
        
        # Use Claude if available, otherwise create simple summary
        if self.anthropic_client:
            return self._claude_summarize(clean_desc, max_words)
        else:
            return self._simple_summarize(clean_desc, max_words)
    
    def _claude_summarize(self, description: str, max_words: int) -> str:
        """Use Claude to create engaging video script"""
        prompt = f"""
        Create an engaging 40-second video script for a gaming recommendation video based on this game description.
        
        Requirements:
        - Maximum {max_words} words
        - Hook the viewer in the first 5 seconds
        - Highlight the most exciting/unique aspects
        - Use enthusiastic, engaging tone
        - End with a call-to-action to check out the game
        - Don't mention specific prices or release dates
        - Make it sound like a friend recommending a game
        
        Game Description:
        {description[:1000]}...
        
        Script:
        """
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            script = response.content[0].text.strip()
            
            # Ensure it's within word limit
            words = script.split()
            if len(words) > max_words:
                script = ' '.join(words[:max_words]) + "..."
            
            logger.info(f"Generated script with {len(script.split())} words")
            return script
            
        except Exception as e:
            logger.error(f"Error with Claude API: {e}")
            return self._simple_summarize(description, max_words)
    
    def _simple_summarize(self, description: str, max_words: int) -> str:
        """Create simple summary without AI"""
        words = description.split()
        
        # Take first portion and clean it up
        summary_words = words[:max_words]
        summary = ' '.join(summary_words)
        
        # Remove incomplete sentences at the end
        sentences = summary.split('.')
        if len(sentences) > 1:
            summary = '. '.join(sentences[:-1]) + '.'
        
        # Add engaging intro if too short
        if len(summary.split()) < 20:
            summary = f"Check out this amazing game! {summary}"
        
        return summary
    
    def generate_voiceover(self, script: str, voice_name: str = None) -> Optional[str]:
        """
        Generate voiceover from script using ElevenLabs
        Returns path to generated audio file
        """
        if not script:
            logger.error("No script provided for voiceover")
            return None
        
        try:
            # Select voice
            selected_voice = self._select_voice(voice_name)
            if not selected_voice:
                logger.error("No suitable voice found")
                return None
            
            # Generate audio
            audio = generate(
                text=script,
                voice=selected_voice,
                model=self.voice_model
            )
            
            # Create output filename
            import time
            timestamp = int(time.time())
            filename = f"voiceover_{timestamp}.mp3"
            filepath = os.path.join(config.TEMP_DIR, filename)
            
            # Ensure temp directory exists
            os.makedirs(config.TEMP_DIR, exist_ok=True)
            
            # Save audio file
            save(audio, filepath)
            
            logger.info(f"Generated voiceover: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating voiceover: {e}")
            return None
    
    def _select_voice(self, voice_name: str = None) -> Optional[Voice]:
        """Select appropriate voice for content"""
        available_voices = self._get_available_voices()
        
        if not available_voices:
            return None
        
        # If specific voice requested, try to find it
        if voice_name:
            for voice in available_voices:
                if voice.name.lower() == voice_name.lower():
                    return voice
        
        # Default to first available voice or specific preferred voices
        preferred_voices = ['Adam', 'Josh', 'Arnold', 'Antoni', 'Sam']
        
        for preferred in preferred_voices:
            for voice in available_voices:
                if voice.name == preferred:
                    logger.info(f"Selected voice: {voice.name}")
                    return voice
        
        # Fall back to first available voice
        if available_voices:
            selected = available_voices[0]
            logger.info(f"Using fallback voice: {selected.name}")
            return selected
        
        return None
    
    def get_voice_info(self) -> Dict:
        """Get information about available voices"""
        voices_list = self._get_available_voices()
        
        voice_info = []
        for voice in voices_list:
            voice_info.append({
                'name': voice.name,
                'voice_id': voice.voice_id,
                'category': getattr(voice, 'category', 'Unknown'),
                'description': getattr(voice, 'description', '')
            })
        
        return {
            'total_voices': len(voice_info),
            'voices': voice_info
        }
    
    def estimate_speech_duration(self, text: str, words_per_minute: int = 150) -> float:
        """Estimate speech duration in seconds"""
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        duration_seconds = duration_minutes * 60
        
        return duration_seconds
    
    def adjust_script_for_duration(self, script: str, target_duration: int = 40) -> str:
        """Adjust script length to fit target duration"""
        current_duration = self.estimate_speech_duration(script)
        
        if current_duration <= target_duration:
            return script
        
        # Calculate target word count
        words_per_second = 150 / 60  # 150 words per minute
        target_words = int(target_duration * words_per_second)
        
        words = script.split()
        if len(words) > target_words:
            # Truncate and try to end on complete sentence
            truncated = ' '.join(words[:target_words])
            sentences = truncated.split('.')
            if len(sentences) > 1:
                truncated = '. '.join(sentences[:-1]) + '.'
            
            logger.info(f"Adjusted script from {len(words)} to {len(truncated.split())} words")
            return truncated
        
        return script 