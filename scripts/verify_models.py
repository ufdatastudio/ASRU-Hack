"""
Verify that model weights have been downloaded.

This script checks if the models are cached locally without loading them into memory.
"""
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HF_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

def check_model_cached(model_id: str, model_name: str) -> bool:
    """Check if a model is cached locally."""
    # HuggingFace converts model IDs to cache directory names
    # Format: models--org--model-name
    cache_name = model_id.replace("/", "--")
    model_cache_dir = HF_CACHE_DIR / f"models--{cache_name}"
    
    if not model_cache_dir.exists():
        logger.warning(f"✗ {model_name}: Not found in cache")
        logger.info(f"  Expected location: {model_cache_dir}")
        return False
    
    # Check for model files (weights)
    model_files = list(model_cache_dir.rglob("*.safetensors"))
    model_files.extend(list(model_cache_dir.rglob("*.bin")))
    model_files.extend(list(model_cache_dir.rglob("*.pt")))
    
    if not model_files:
        logger.warning(f"✗ {model_name}: Cache directory exists but no weight files found")
        return False
    
    # Calculate total size
    total_size = sum(f.stat().st_size for f in model_files)
    size_gb = total_size / (1024 ** 3)
    
    logger.info(f"✓ {model_name}: Cached")
    logger.info(f"  Location: {model_cache_dir}")
    logger.info(f"  Weight files: {len(model_files)}")
    logger.info(f"  Total size: {size_gb:.2f} GB")
    
    return True

def main():
    logger.info("=" * 60)
    logger.info("Verifying Model Downloads")
    logger.info("=" * 60)
    logger.info("")
    
    logger.info(f"Checking HuggingFace cache: {HF_CACHE_DIR}")
    logger.info("")
    
    results = {}
    
    # Check MMS-TTS
    results['mms_tts'] = check_model_cached(
        "facebook/mms-tts-yor",
        "Meta MMS-TTS Yoruba"
    )
    
    logger.info("")
    
    # Check AF3
    results['af3'] = check_model_cached(
        "nvidia/audio-flamingo-3-chat",
        "Audio Flamingo 3"
    )
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("Summary")
    logger.info("=" * 60)
    
    if results['mms_tts']:
        logger.info("✓ MMS-TTS: Ready")
    else:
        logger.info("✗ MMS-TTS: Not downloaded")
    
    if results['af3']:
        logger.info("✓ AF3: Ready")
    else:
        logger.info("✗ AF3: Not downloaded")
    
    logger.info("")
    
    if all(results.values()):
        logger.info("All models are downloaded and ready!")
        logger.info("You can now start the server.")
    else:
        logger.info("Some models are missing.")
        logger.info("Run: bash scripts/download_models.sh")

if __name__ == "__main__":
    main()

