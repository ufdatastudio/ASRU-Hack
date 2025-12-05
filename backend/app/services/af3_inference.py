"""
Audio Flamingo 3 (AF3) Inference Module
Loads AF3 from local path (or HuggingFace as fallback) and processes audio to text.
"""
import os
import sys
import torch
import logging
import numpy as np
from typing import Tuple, Optional
import soundfile as sf
import io

# Import config for local model path
from backend.config import AUDIO_FLAMINGO_MODEL_PATH, AUDIO_FLAMINGO_ROOT

logger = logging.getLogger(__name__)

# Global model instance
af3_model = None
af3_processor = None


def load_af3():
    """
    Load Audio Flamingo 3 model from local path (or HuggingFace as fallback).
    Returns (model, processor) tuple.
    """
    global af3_model, af3_processor
    
    if af3_model is not None and af3_processor is not None:
        logger.info("AF3 model already loaded, returning existing instance")
        return (af3_model, af3_processor)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if device == "cuda" else torch.float32
    
    logger.info(f"Loading model on {device} with dtype {torch_dtype}")
    
    # Try loading from local path first
    if os.path.exists(AUDIO_FLAMINGO_MODEL_PATH):
        logger.info(f"Found local Audio Flamingo 3 model at: {AUDIO_FLAMINGO_MODEL_PATH}")
        logger.info("Loading from local path (using llava module)...")
        
        try:
            # Add Audio Flamingo root to path to import llava
            if AUDIO_FLAMINGO_ROOT not in sys.path:
                sys.path.insert(0, AUDIO_FLAMINGO_ROOT)
            
            import llava
            from llava import conversation as clib
            from llava.media import Sound
            from transformers import GenerationConfig
            
            # Load model using llava.load() (local loading method)
            load_kwargs = {"device": device}
            if device == "cpu":
                load_kwargs["torch_dtype"] = torch.float32
            else:
                load_kwargs["torch_dtype"] = torch_dtype
            
            logger.info(f"Loading model from {AUDIO_FLAMINGO_MODEL_PATH}...")
            af3_model = llava.load(AUDIO_FLAMINGO_MODEL_PATH, **load_kwargs)
            
            # Load generation config if available
            generation_config_path = os.path.join(AUDIO_FLAMINGO_MODEL_PATH, 'llm')
            if os.path.exists(os.path.join(generation_config_path, 'generation_config.json')):
                af3_model.generation_config = GenerationConfig.from_pretrained(generation_config_path)
            
            # Set conversation template
            clib.default_conversation = clib.conv_templates.get("auto", clib.conv_templates["default"]).copy()
            
            # Create a processor-like wrapper for compatibility
            # The llava model uses Sound() directly, so we create a simple wrapper
            class LocalProcessor:
                def __init__(self, model):
                    self.model = model
                
                def __call__(self, audios=None, return_tensors="pt", **kwargs):
                    # Compatibility wrapper for llava-style processing
                    return {"audio_input": audios}
                
                def batch_decode(self, outputs, skip_special_tokens=True):
                    # For local llava model, outputs are already text
                    if isinstance(outputs, str):
                        return [outputs]
                    return outputs if isinstance(outputs, list) else [str(outputs)]
            
            af3_processor = LocalProcessor(af3_model)
            
            logger.info("✓ Audio Flamingo 3 loaded successfully from local path!")
            return (af3_model, af3_processor)
            
        except Exception as e:
            logger.warning(f"Failed to load from local path: {e}")
            logger.info("Falling back to HuggingFace...")
            # Fall through to HuggingFace loading
    
    # Fallback: Try loading from HuggingFace
    logger.info("Loading Audio Flamingo 3 from HuggingFace (nvidia/audio-flamingo-3-chat)...")
    logger.info("(This will download model weights if not cached)")
    
    try:
        # Try importing audio-flamingo package
        try:
            from audio_flamingo import FlamingoForConditionalGeneration, FlamingoProcessor
        except ImportError:
            logger.error("audio-flamingo package not found and local model unavailable.")
            logger.error("Install with: uv pip install git+https://github.com/NVIDIA/audio-flamingo-3")
            raise ImportError("audio-flamingo package is required when local model is not available.")
        
        # Load model and processor from HuggingFace
        af3_model = FlamingoForConditionalGeneration.from_pretrained(
            "nvidia/audio-flamingo-3-chat",
            torch_dtype=torch_dtype,
            device_map="auto" if device == "cuda" else None
        )
        
        if device == "cpu":
            af3_model = af3_model.to(device)
        
        af3_processor = FlamingoProcessor.from_pretrained("nvidia/audio-flamingo-3-chat")
        
        logger.info("✓ Audio Flamingo 3 loaded successfully from HuggingFace!")
        return (af3_model, af3_processor)
        
    except Exception as e:
        logger.error(f"Failed to load AF3 model: {e}", exc_info=True)
        raise


def run_af3(model, processor, audio_input) -> str:
    """
    Run AF3 inference on audio input.
    Supports both local llava model and HuggingFace model.
    
    Args:
        model: Model instance (llava model or FlamingoForConditionalGeneration)
        processor: Processor instance (LocalProcessor wrapper or FlamingoProcessor)
        audio_input: Can be:
            - str: Path to audio file (preferred for local llava model)
            - np.ndarray: Audio waveform array
            - bytes: WAV audio bytes
            - torch.Tensor: Audio tensor
    
    Returns:
        str: Text response from AF3
    """
    try:
        # Check if this is the local llava model (has generate_content method)
        is_local_model = hasattr(model, 'generate_content')
        
        if is_local_model:
            # Local llava model path
            if isinstance(audio_input, str):
                # Direct file path - llava model prefers this
                logger.info(f"Processing audio file with local AF3: {audio_input}")
                
                try:
                    from llava.media import Sound
                    # Create prompt with audio
                    prompt = [Sound(audio_input)]
                    
                    # Generate response using llava model
                    response = model.generate_content(
                        prompt,
                        generation_config=getattr(model, 'generation_config', None)
                    )
                    
                    logger.info(f"AF3 response: {response[:100]}...")  # Log first 100 chars
                    return response
                    
                except Exception as e:
                    logger.error(f"Error with local model audio processing: {e}", exc_info=True)
                    raise
            else:
                # For local model, if not a file path, save to temp file first
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    if isinstance(audio_input, bytes):
                        tmp_file.write(audio_input)
                    elif isinstance(audio_input, (np.ndarray, torch.Tensor)):
                        sf.write(tmp_file.name, np.array(audio_input), 16000)
                    tmp_path = tmp_file.name
                
                try:
                    from llava.media import Sound
                    prompt = [Sound(tmp_path)]
                    response = model.generate_content(
                        prompt,
                        generation_config=getattr(model, 'generation_config', None)
                    )
                    return response
                finally:
                    os.unlink(tmp_path)
        
        else:
            # HuggingFace model path (standard transformers API)
            # Convert audio input to tensor format
            if isinstance(audio_input, str):
                # Load audio file
                audio_data, sample_rate = sf.read(audio_input)
                audio_tensor = torch.from_numpy(audio_data).float()
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)  # Add channel dimension if mono
            
            elif isinstance(audio_input, bytes):
                # Load from bytes (WAV format)
                audio_file = io.BytesIO(audio_input)
                audio_data, sample_rate = sf.read(audio_file)
                audio_tensor = torch.from_numpy(audio_data).float()
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)
            
            elif isinstance(audio_input, np.ndarray):
                audio_tensor = torch.from_numpy(audio_input).float()
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)
            
            elif isinstance(audio_input, torch.Tensor):
                audio_tensor = audio_input.float()
                if len(audio_tensor.shape) == 1:
                    audio_tensor = audio_tensor.unsqueeze(0)
            else:
                raise ValueError(f"Unsupported audio input type: {type(audio_input)}")
            
            logger.info(f"Processing audio with HuggingFace AF3 - shape: {audio_tensor.shape}")
            
            # Process audio through AF3
            device = next(model.parameters()).device
            audio_tensor = audio_tensor.to(device)
            
            # Prepare inputs using processor
            inputs = processor(audios=audio_tensor, return_tensors="pt")
            inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=512)
            
            # Decode output
            text_response = processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            logger.info(f"AF3 response: {text_response[:100]}...")  # Log first 100 chars
            return text_response
        
    except Exception as e:
        logger.error(f"Error running AF3 inference: {e}", exc_info=True)
        return f"I encountered an error processing your audio: {str(e)}"

