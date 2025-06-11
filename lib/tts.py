"""
Text-to-speech processing using Chatterbox
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from .config import config
from .utils import create_safe_name

logger = logging.getLogger(__name__)

class TTSProcessor:
    """Handles text-to-speech generation using Chatterbox"""
    
    def __init__(self):
        self.temp_dir = config.get_directory("temp")
        self.model_settings = config.get("tts", {})
        
    def generate_audio(self, script: str, game_name: Optional[str] = None) -> Tuple[bool, Optional[str], float]:
        """
        Generate TTS audio from script
        
        Args:
            script: Text to convert to speech
            game_name: Game name for file naming (optional)
            
        Returns:
            Tuple of (success, audio_file_path, duration)
        """
        if not script:
            logger.error("No script provided for TTS")
            return False, None, 0.0
        
        try:
            # Import TTS dependencies
            from chatterbox.tts import ChatterboxTTS
            import torch
            import torchaudio
            
            logger.info("[TTS] Generating TTS audio...")
            
            # Setup device and patch torch.load for CPU compatibility
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Patch torch.load to force CPU mapping if CUDA is not available
            if not torch.cuda.is_available():
                original_load = torch.load
                def patched_load(*args, **kwargs):
                    kwargs['map_location'] = torch.device('cpu')
                    return original_load(*args, **kwargs)
                torch.load = patched_load
                logger.info("[TTS] Patched torch.load for CPU compatibility")
            
            # Load model
            model = ChatterboxTTS.from_pretrained(device=device)
            
            # Restore original torch.load if we patched it
            if not torch.cuda.is_available() and 'original_load' in locals():
                torch.load = original_load
            
            # Clean script for better TTS
            clean_script = script.replace('\n', ' ').strip()
            
            # Generate audio with configured settings
            wav = model.generate(
                clean_script,
                exaggeration=self.model_settings.get("exaggeration", 0.3),
                cfg_weight=self.model_settings.get("cfg_weight", 0.5),
                temperature=self.model_settings.get("temperature", 0.85)
            )
            
            # Create output path
            if game_name:
                safe_name = create_safe_name(game_name)
                output_path = self.temp_dir / f"{safe_name}_audio.wav"
            else:
                output_path = self.temp_dir / f"tts_audio_{int(time.time())}.wav"
            
            # Ensure temp directory exists
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save audio
            torchaudio.save(str(output_path), wav, model.sr)
            
            # Verify file exists and get duration
            if output_path.exists():
                info = torchaudio.info(str(output_path))
                duration = info.num_frames / info.sample_rate
                
                logger.info(f"[SUCCESS] TTS audio created: {duration:.1f}s at {output_path}")
                return True, str(output_path), duration
            else:
                logger.error("[ERROR] TTS file not created")
                return False, None, 0.0
                
        except ImportError as e:
            logger.error(f"[ERROR] TTS dependencies not available: {e}")
            logger.info("[FALLBACK] Attempting alternative TTS method...")
            return self._fallback_tts_generation(script, game_name)
        except Exception as e:
            logger.error(f"[ERROR] TTS generation failed: {e}")
            logger.info("[FALLBACK] Attempting alternative TTS method...")
            return self._fallback_tts_generation(script, game_name)
    
    def estimate_duration(self, text: str) -> float:
        """Estimate speech duration in seconds"""
        words_per_minute = self.model_settings.get("words_per_minute", 180)
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        return duration_minutes * 60
    
    def adjust_script_for_duration(self, script: str, target_duration: float) -> str:
        """Adjust script length to fit target duration"""
        current_duration = self.estimate_duration(script)
        
        if current_duration <= target_duration:
            return script
        
        # Calculate target word count
        words_per_minute = self.model_settings.get("words_per_minute", 180)
        words_per_second = words_per_minute / 60
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
    
    def _fallback_tts_generation(self, script: str, game_name: Optional[str] = None) -> Tuple[bool, Optional[str], float]:
        """Fallback TTS generation using pyttsx3 or creating a placeholder"""
        try:
            # Try pyttsx3 as fallback
            import pyttsx3
            
            logger.info("[FALLBACK] Using pyttsx3 for TTS generation...")
            
            # Create output path
            if game_name:
                safe_name = create_safe_name(game_name)
                output_path = self.temp_dir / f"{safe_name}_audio.wav"
            else:
                output_path = self.temp_dir / f"tts_audio_{int(time.time())}.wav"
            
            # Initialize pyttsx3
            engine = pyttsx3.init()
            
            # Set properties
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)  # Use first available voice
            
            engine.setProperty('rate', 150)  # Speaking rate
            engine.setProperty('volume', 0.9)  # Volume level
            
            # Save to file
            engine.save_to_file(script, str(output_path))
            engine.runAndWait()
            
            if output_path.exists():
                # Estimate duration (pyttsx3 doesn't provide duration info)
                duration = self.estimate_duration(script)
                logger.info(f"[FALLBACK] TTS audio created: {duration:.1f}s at {output_path}")
                return True, str(output_path), duration
            else:
                logger.error("[FALLBACK] pyttsx3 failed to create audio file")
                return self._create_placeholder_audio(script, game_name)
                
        except ImportError:
            logger.warning("[FALLBACK] pyttsx3 not available, creating placeholder audio")
            return self._create_placeholder_audio(script, game_name)
        except Exception as e:
            logger.error(f"[FALLBACK] pyttsx3 failed: {e}")
            return self._create_placeholder_audio(script, game_name)
    
    def _create_placeholder_audio(self, script: str, game_name: Optional[str] = None) -> Tuple[bool, Optional[str], float]:
        """Create a placeholder audio file when TTS is not available"""
        try:
            # Create output path
            if game_name:
                safe_name = create_safe_name(game_name)
                output_path = self.temp_dir / f"{safe_name}_audio_placeholder.txt"
            else:
                output_path = self.temp_dir / f"tts_audio_placeholder_{int(time.time())}.txt"
            
            # Ensure temp directory exists
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create placeholder file with script
            duration = self.estimate_duration(script)
            placeholder_content = f"""
PLACEHOLDER AUDIO FILE
======================

This is a placeholder for TTS audio that would be generated with the following script:

"{script}"

Estimated duration: {duration:.1f} seconds
Target words per minute: {self.model_settings.get('words_per_minute', 180)}

To enable actual TTS generation, install the required dependencies:
- pip install chatterbox
- pip install torch torchaudio

Or install pyttsx3 for basic TTS:
- pip install pyttsx3
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            logger.warning(f"[PLACEHOLDER] Created placeholder audio file: {output_path}")
            logger.warning("[PLACEHOLDER] Install TTS dependencies for actual audio generation")
            
            return True, str(output_path), duration
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create placeholder audio: {e}")
            return False, None, 0.0
    
    def cleanup_audio_file(self, audio_path: str):
        """Clean up temporary audio file"""
        try:
            if audio_path and Path(audio_path).exists():
                Path(audio_path).unlink()
                logger.debug(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup audio file {audio_path}: {e}")

import time
from .utils import create_safe_name