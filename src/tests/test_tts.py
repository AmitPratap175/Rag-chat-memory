import os
import wave
import asyncio # Required for running async functions
import logging
from typing import Optional
from ai_companion.settings import settings

# --- Mocking external dependencies for demonstration ---
class TextToSpeechError(Exception):
    """Custom exception for text-to-speech errors."""
    pass


# End of Mocking ---

# Import the core Google GenAI client and types
from google.genai import Client as TTSGenerator
from google.genai import types


class TextToSpeech:
    """A class to handle text-to-speech conversion using Gemini TTS model."""

    # Required environment variables (checked via settings object now)
    REQUIRED_ENV_VARS = ["GOOGLE_API_KEY"] # This is more for documentation

    def __init__(self):
        """Initialize the TextToSpeech class and validate environment variables."""
        # Validate that GOOGLE_API_KEY is accessible, either from env or settings
        if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "YOUR_ACTUAL_GOOGLE_API_KEY_HERE":
            raise ValueError(
                "GOOGLE_API_KEY is not set. Please set it as an environment variable or in your MockSettings class."
            )

        self._client: Optional[TTSGenerator] = None
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @property
    def client(self) -> TTSGenerator:
        """Get or create Gemini TTS model client instance using singleton pattern."""
        if self._client is None:
            self._client = TTSGenerator(api_key=settings.GOOGLE_API_KEY)
        return self._client

    def synthesize(self, text: str) -> bytes:
        """Convert text to speech using Gemini TTS model.

        Args:
            text (str): Text to convert to speech.

        Returns:
            bytes: Audio data in WAV format.

        Raises:
            ValueError: If the input text is empty or too long.
            TextToSpeechError: If the text-to-speech conversion fails or returns empty audio.
        """
        print("Text----------->",text)
        if not text.strip():
            raise ValueError("Input text cannot be empty")

        # Gemini TTS model typical limit (adjust if documentation changes)
        if len(text) > 5000:
            raise ValueError("Input text exceeds maximum length of 5000 characters")

        self.logger.info(f"Attempting to synthesize text: '{text[:50]}...'")

        try:
            # Call the Gemini model for content generation with AUDIO modality
            response = self.client.models.generate_content( # Use await for async call
                model=settings.TTS_MODEL_NAME,
                contents=text, # Pass the text directly as contents
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Kore', # Example voice. You can choose others.
                            )
                        )
                    ),
                )
            )

            audio_data = response.candidates[0].content.parts[0].inline_data.data

            if not audio_data:
                raise TextToSpeechError("Generated audio is empty or not found in the expected format.")

            self.logger.info(f"Text-to-speech conversion successful. Audio size: {len(audio_data)} bytes.")
            return audio_data

        except Exception as e:
            self.logger.error(f"Text-to-speech conversion failed: {str(e)}")
            raise TextToSpeechError(f"Text-to-speech conversion failed: {str(e)}") from e


# Helper function to save PCM data to a WAV file
def save_wav_file(filename: str, pcm: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> None:
   """
   Saves raw PCM audio data to a WAV file.

   Args:
       filename (str): The name of the output WAV file.
       pcm (bytes): The raw PCM audio data.
       channels (int): Number of audio channels (e.g., 1 for mono, 2 for stereo).
       rate (int): Sample rate (samples per second).
       sample_width (int): Sample width in bytes (e.g., 2 for 16-bit audio).
   """
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)
   print(f"Audio saved to {filename}")


# --- Main execution block for testing the TextToSpeech class ---
if __name__ == "__main__":
    def run_tts_example():
        print("Initializing TextToSpeech class...")
        try:
            tts_converter = TextToSpeech()
            print("TextToSpeech class initialized successfully.")
        except ValueError as e:
            print(f"Initialization failed: {e}")
            print("Please ensure your GOOGLE_API_KEY environment variable is set or updated in MockSettings.")
            return

        print("\n--- Testing Text-to-Speech Conversion ---")
        test_text_1 = "Hello, this is a test of the Gemini text-to-speech model. I hope you are having a wonderful day!"
        output_file_1 = "gemini_tts_output_1.wav"

        test_text_2 = "The quick brown fox jumps over the lazy dog."
        output_file_2 = "gemini_tts_output_2.wav"

        try:
            print(f"Synthesizing: '{test_text_1}'")
            audio_data_1 = tts_converter.synthesize(test_text_1)
            save_wav_file(output_file_1, audio_data_1)
        except TextToSpeechError as e:
            print(f"Error during TTS synthesis 1: {e}")
        except ValueError as e:
            print(f"Input error for TTS synthesis 1: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during TTS synthesis 1: {e}")

        # print("\n--- Testing another Text-to-Speech Conversion ---")
        # try:
        #     print(f"Synthesizing: '{test_text_2}'")
        #     audio_data_2 = await tts_converter.synthesize(test_text_2)
        #     save_wav_file(output_file_2, audio_data_2)
        # except TextToSpeechError as e:
        #     print(f"Error during TTS synthesis 2: {e}")
        # except ValueError as e:
        #     print(f"Input error for TTS synthesis 2: {e}")
        # except Exception as e:
        #     print(f"An unexpected error occurred during TTS synthesis 2: {e}")

        # print("\n--- Testing error handling for empty text ---")
        # try:
        #     await tts_converter.synthesize("")
        # except ValueError as e:
        #     print(f"Caught expected error for empty text: {e}")
        # except Exception as e:
        #     print(f"Caught unexpected error for empty text: {e}")

        # print("\n--- Testing error handling for long text ---")
        # long_text = "a" * 5001
        # try:
        #     await tts_converter.synthesize(long_text)
        # except ValueError as e:
        #     print(f"Caught expected error for long text: {e}")
        # except Exception as e:
        #     print(f"Caught unexpected error for long text: {e}")


    # Run the asynchronous example function
    run_tts_example()