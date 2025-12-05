"""
Download models for African Health Studio Backend

This script pre-downloads all required models from HuggingFace:
1. Audio Flamingo 3 (nvidia/audio-flamingo-3-chat)
2. Meta MMS-TTS Yoruba (facebook/mms-tts-yor)

Models will be cached in HuggingFace cache directory (~/.cache/huggingface/)
"""
import os
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_af3_model():
    """Download Audio Flamingo 3 model."""
    logger.info("=" * 60)
    logger.info("Downloading Audio Flamingo 3 (AF3)")
    logger.info("=" * 60)
    
    try:
        # Try importing audio-flamingo
        try:
            from audio_flamingo import FlamingoForConditionalGeneration, FlamingoProcessor
        except ImportError:
            logger.error("audio-flamingo package not found!")
            logger.error("Install with: uv pip install git+https://github.com/NVIDIA/audio-flamingo-3")
            logger.error("Or add to pyproject.toml: audio-flamingo @ git+https://github.com/NVIDIA/audio-flamingo-3")
            return False
        
        logger.info("Loading AF3 model from HuggingFace: nvidia/audio-flamingo-3-chat")
        logger.info("This will download model weights (~10-20GB) if not already cached...")
        logger.info("Download location: ~/.cache/huggingface/hub/models--nvidia--audio-flamingo-3-chat/")
        logger.info("This may take 30-60 minutes depending on your connection...")
        
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32
        
        logger.info(f"Device: {device}, dtype: {torch_dtype}")
        logger.info("")
        logger.info("Downloading model weights (this may take a while)...")
        
        # Download model weights - from_pretrained() automatically downloads if not cached
        model = FlamingoForConditionalGeneration.from_pretrained(
            "nvidia/audio-flamingo-3-chat",
            torch_dtype=torch_dtype,
            device_map="auto" if device == "cuda" else None
        )
        
        if device == "cpu":
            model = model.to(device)
        
        logger.info("Downloading processor/tokenizer files...")
        # Download processor - this also downloads config and tokenizer files
        processor = FlamingoProcessor.from_pretrained("nvidia/audio-flamingo-3-chat")
        
        logger.info("✓ Audio Flamingo 3 downloaded and cached successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download AF3: {e}", exc_info=True)
        return False


def download_mms_tts_model():
    """Download Meta MMS-TTS Yoruba model."""
    logger.info("=" * 60)
    logger.info("Downloading Meta MMS-TTS Yoruba")
    logger.info("=" * 60)
    
    try:
        from transformers import VitsModel, AutoTokenizer
        
        logger.info("Loading MMS-TTS model from HuggingFace: facebook/mms-tts-yor")
        logger.info("This will download model weights (~100-200MB) if not already cached...")
        logger.info("Download location: ~/.cache/huggingface/hub/models--facebook--mms-tts-yor/")
        logger.info("This may take 2-5 minutes depending on your connection...")
        
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Device: {device}")
        logger.info("")
        logger.info("Downloading model weights...")
        
        # Download model weights - from_pretrained() automatically downloads if not cached
        model = VitsModel.from_pretrained("facebook/mms-tts-yor")
        model = model.to(device)
        model.eval()
        
        logger.info("Downloading tokenizer/config files...")
        # Download tokenizer - this also downloads config files
        tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-yor")
        
        logger.info("✓ Meta MMS-TTS Yoruba downloaded and cached successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download MMS-TTS: {e}", exc_info=True)
        return False


def main():
    """Download all models."""
    logger.info("=" * 60)
    logger.info("African Health Studio - Model Download Script")
    logger.info("=" * 60)
    logger.info("")
    
    # Check if running on GPU
    import torch
    if torch.cuda.is_available():
        logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA version: {torch.version.cuda}")
    else:
        logger.info("GPU not available, will use CPU (slower)")
    
    logger.info("")
    logger.info("Models will be downloaded and cached in: ~/.cache/huggingface/hub/")
    logger.info("")
    logger.info("What gets downloaded:")
    logger.info("  - Model weights (.safetensors or .bin files)")
    logger.info("  - Configuration files (config.json)")
    logger.info("  - Tokenizer files (tokenizer.json, vocab files)")
    logger.info("  - Other model artifacts")
    logger.info("")
    
    results = {}
    
    # Download MMS-TTS first (smaller, faster)
    logger.info("Starting with MMS-TTS (smaller model)...")
    results['mms_tts'] = download_mms_tts_model()
    
    logger.info("")
    
    # Ask about AF3 (large download)
    download_af3 = input("\nDownload Audio Flamingo 3? (This is a large model ~10-20GB) [y/N]: ").strip().lower()
    
    if download_af3 in ['y', 'yes']:
        results['af3'] = download_af3_model()
    else:
        logger.info("Skipping AF3 download. You can download it later or it will download on first use.")
        results['af3'] = None
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Download Summary")
    logger.info("=" * 60)
    
    if results['mms_tts']:
        logger.info("✓ MMS-TTS: Downloaded")
    else:
        logger.info("✗ MMS-TTS: Failed")
    
    if results['af3'] is True:
        logger.info("✓ AF3: Downloaded")
    elif results['af3'] is False:
        logger.info("✗ AF3: Failed")
    else:
        logger.info("- AF3: Skipped")
    
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Models are cached and ready to use")
    logger.info("2. Run the server: bash run_server_interactive.sh or sbatch run_server.slurm")
    logger.info("3. Models will load automatically on server startup")


if __name__ == "__main__":
    main()

