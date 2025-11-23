import os
import torch
import logging
import sys

# Ensure the config is imported first to set up sys.path
from backend.config import AUDIO_FLAMINGO_MODEL_PATH, TEMP_AUDIO_DIR

# Now we can try to import llava. 
try:
    import llava
    from llava import conversation as clib
    from llava.media import Sound
    from peft import PeftModel
    from transformers import GenerationConfig
except ImportError as e:
    logging.error(f"Failed to import llava. Make sure AUDIO_FLAMINGO_ROOT is correct in config.py. Error: {e}")
    llava = None

logger = logging.getLogger(__name__)

class AudioFlamingoService:
    def __init__(self, model_path=AUDIO_FLAMINGO_MODEL_PATH, conv_mode="auto", think_mode=False):
        if llava is None:
            raise RuntimeError("Audio Flamingo (llava) module not found.")
        
        self.model_path = model_path
        self.conv_mode = conv_mode
        self.think_mode = think_mode
        self.model = None
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing AudioFlamingoService on {self.device}...")
        
        logger.info(f"Loading Audio Flamingo 3 from {model_path}...")
        self._load_model()
        logger.info("Audio Flamingo 3 loaded successfully.")

    def _load_model(self):
        load_kwargs = {"device": self.device}
        
        if self.device == "cpu":
            # Force float32 for CPU to avoid float16 unimplemented errors
            load_kwargs["torch_dtype"] = torch.float32
            logger.warning("CUDA not available. Forcing CPU mode (will be slow).")
        
        # Load the base model
        # Passing device and dtype via kwargs to llava.load -> load_pretrained_model
        self.model = llava.load(self.model_path, **load_kwargs)
        
        # Load generation config if available
        generation_config_path = os.path.join(self.model_path, 'llm')
        if os.path.exists(os.path.join(generation_config_path, 'generation_config.json')):
            self.model.generation_config = GenerationConfig.from_pretrained(generation_config_path)
        
        # Load think mode adapter if requested
        if self.think_mode:
            model_think = os.path.join(self.model_path, 'stage35')
            if os.path.exists(model_think):
                logger.info("Loading think-mode adapter...")
                self.model = PeftModel.from_pretrained(
                    self.model,
                    model_think,
                    device_map="auto" if self.device == "cuda" else {"": "cpu"},
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                )
            else:
                logger.warning(f"Think mode requested but adapter not found at {model_think}")

        # Set conversation template
        if self.conv_mode in clib.conv_templates:
            clib.default_conversation = clib.conv_templates[self.conv_mode].copy()
        else:
            logger.warning(f"Conversation mode '{self.conv_mode}' not found, using default.")

    def process_audio(self, audio_path: str, text_prompt: str = None):
        """
        Process an audio file and return the text response.
        """
        if not self.model:
            raise RuntimeError("Model not loaded.")

        prompt = []
        
        # Add audio to prompt
        try:
            media = Sound(audio_path)
            prompt.append(media)
        except Exception as e:
            logger.error(f"Error loading sound file {audio_path}: {e}")
            return "Error processing audio file."

        # Add text prompt
        if text_prompt:
            prompt.append(text_prompt)
        else:
            # Default system prompt logic could go here
            pass
            
        logger.info(f"Generating response for audio: {audio_path}")
        
        # Generate response
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.model.generation_config
            )
            return response
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return "I'm sorry, I encountered an error processing your request."

    def reset_conversation(self):
        """
        Resets the conversation history.
        """
        if self.conv_mode in clib.conv_templates:
            clib.default_conversation = clib.conv_templates[self.conv_mode].copy()
