"""
Transcription Service - Cross-Platform GPU-Accelerated Audio Transcription

This module provides audio transcription using faster-whisper with automatic
GPU detection and platform-specific acceleration (CUDA/Metal/CPU).

Version: 2.1 (Production-Ready with cuDNN Fallback)
Date: November 7, 2025
"""

# CRITICAL: Disable cuDNN BEFORE any PyTorch/CUDA imports
# This prevents cuDNN symbol lookup crashes when cuDNN is not installed
import os
os.environ["CUDA_MODULE_LOADING"] = "LAZY"  # Lazy load CUDA modules

import sys
from typing import Dict, Optional, List, Tuple
from pathlib import Path

# Now safe to import PyTorch
import torch

# Disable cuDNN to avoid symbol loading issues
torch.backends.cudnn.enabled = False
torch.backends.cudnn.benchmark = False

# Import faster-whisper for GPU-accelerated transcription
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    print("[WARNING] faster-whisper not installed. Install with: pip install faster-whisper")
    FASTER_WHISPER_AVAILABLE = False

# Import platform utilities for GPU detection
try:
    from .platform_utils import (
        get_compute_device,
        get_system_info,
        get_cuda_memory_info,
        estimate_transcription_speed
    )
    PLATFORM_UTILS_AVAILABLE = True
except ImportError:
    print("[WARNING] platform_utils.py not found. Using CPU fallback.")
    PLATFORM_UTILS_AVAILABLE = False


# ============================================================================
# Global Variables
# ============================================================================

# Model instance (lazy loading - initialized on first transcription)
model: Optional[WhisperModel] = None
current_device: Optional[str] = None
current_model_size: Optional[str] = None


# ============================================================================
# Diagnostic Functions
# ============================================================================

def print_cuda_diagnostics():
    """Print CUDA/cuDNN diagnostic information for debugging."""
    try:
        print("\n[DIAGNOSTICS] CUDA Environment:")
        print(f"  PyTorch version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  Device count: {torch.cuda.device_count()}")
            print(f"  Device name: {torch.cuda.get_device_name(0)}")
            
        print(f"  cuDNN enabled: {torch.backends.cudnn.enabled}")
        print(f"  cuDNN available: {torch.backends.cudnn.is_available()}")
        if torch.backends.cudnn.is_available():
            print(f"  cuDNN version: {torch.backends.cudnn.version()}")
        print()
        
    except Exception as e:
        print(f"[WARNING] Could not retrieve CUDA diagnostics: {e}")


# ============================================================================
# Model Selection Logic
# ============================================================================

# Model size recommendations based on GPU memory
MODEL_SIZES = {
    "tiny": "Fastest, least accurate (39M params, ~1GB RAM)",
    "base": "Fast, decent accuracy (74M params, ~1GB RAM)",
    "small": "Balanced (244M params, ~2GB RAM)",
    "medium": "Good accuracy (769M params, ~5GB RAM)",
    "large-v2": "High accuracy (1550M params, ~10GB RAM)",
    "large-v3": "Best accuracy (1550M params, ~10GB RAM)"
}

def select_optimal_model_size(device: str, gpu_memory_gb: Optional[float] = None) -> str:
    """
    Select optimal Whisper model size based on available hardware.
    
    Args:
        device: Device type ('cuda', 'mps', or 'cpu')
        gpu_memory_gb: Available GPU memory in GB (if known)
    
    Returns:
        str: Recommended model size
    """
    if device == "cpu":
        return "base"  # Fast enough for CPU
    
    # GPU-accelerated (CUDA or Metal)
    if gpu_memory_gb is None:
        return "small"  # Conservative default
    
    # For 6GB GPU, use small to be safe (medium might OOM during long files)
    if gpu_memory_gb < 4:
        return "small"
    elif gpu_memory_gb < 8:
        return "small"  # Conservative for 6GB cards
    else:
        return "medium"



# ============================================================================
# Preflight Safety Check
# ============================================================================

def _cudnn_ops_loadable() -> bool:
    """Check if cuDNN ops library is loadable to prevent crashes."""
    import ctypes
    for lib in ("libcudnn_ops.so.9.1.0", "libcudnn_ops.so.9.1", 
                "libcudnn_ops.so.9", "libcudnn_ops.so"):
        try:
            ctypes.CDLL(lib)
            return True
        except OSError:
            continue
    return False


# ============================================================================
# Model Management
# ============================================================================

def initialize_model(model_size: str = "auto", device: str = "auto") -> None:
    """
    Initialize the Whisper model with specified size and device.
    
    Implements robust fallback strategy:
    1. Try CUDA (without cuDNN)
    2. Fall back to CPU if CUDA fails
    
    Args:
        model_size: Model size ("auto", "tiny", "base", "small", "medium", "large-v2", "large-v3")
        device: Device ("auto", "cuda", "cpu")
    
    Raises:
        RuntimeError: If model loading fails completely
    """
    global model, current_device, current_model_size
    
    if not FASTER_WHISPER_AVAILABLE:
        raise RuntimeError(
            "faster-whisper is not installed. Install it with:\n"
            "pip install faster-whisper"
        )
    
    # Print diagnostics once
    print_cuda_diagnostics()
    
    # Determine device with preflight
    if device == "auto":
        if PLATFORM_UTILS_AVAILABLE:
            device = get_compute_device()
            # Preflight: check cuDNN before trying CUDA
            if device == "cuda" and not _cudnn_ops_loadable():
                print("[PREFLIGHT] cuDNN not available → using CPU")
                device = "cpu"
            print(f"[AUTO] Detected device: {device}")
        else:
            device = "cpu"
            print("[AUTO] Platform utils unavailable, using CPU")
    
    # Determine model size
    if model_size == "auto":
        if PLATFORM_UTILS_AVAILABLE:
            gpu_memory_gb = None
            
            if device == "cuda":
                memory_info = get_cuda_memory_info()
                if memory_info:
                    gpu_memory_gb = memory_info['total'] / (1024**3)
                    print(f"[AUTO] Detected GPU memory: {gpu_memory_gb:.1f} GB")
            
            model_size = select_optimal_model_size(device, gpu_memory_gb)
            print(f"[AUTO] Selected model size: {model_size}")
        else:
            model_size = "base"
            print(f"[AUTO] Using default model size: {model_size}")
    
    # Try loading with fallback strategy
    load_attempts = []
    
    if device == "cuda":
        load_attempts = [
            ("cuda", "int8_float32", "CUDA GPU (cuDNN disabled)"),
            ("cpu", "int8", "CPU (CUDA failed)")
        ]
    else:
        load_attempts = [
            (device, "int8", f"{device.upper()}")
        ]
    
    last_error = None
    
    for attempt_device, compute_type, description in load_attempts:
        try:
            print(f"[LOADING] Trying: {description}")
            print(f"  Model: {model_size}")
            print(f"  Device: {attempt_device}")
            print(f"  Compute type: {compute_type}")
            
            model = WhisperModel(
                model_size,
                device=attempt_device,
                compute_type=compute_type,
                download_root=os.path.expanduser("~/.cache/whisper")
            )
            
            current_device = attempt_device
            current_model_size = model_size
            
            print(f"✓ Model loaded successfully on {attempt_device}!")
            
            print(f"[PIPELINE] Whisper: {current_device.upper()} | VAD: AUTO | Fallback: CPU on cuDNN error")
            # Display expected performance
            if PLATFORM_UTILS_AVAILABLE and attempt_device == "cuda":
                speed_info = estimate_transcription_speed()
                print(f"  Expected performance: {speed_info['description']}")
            elif attempt_device == "cpu":
                print(f"  Expected performance: 1x real-time (CPU mode)")
            
            return  # Success!
            
        except Exception as e:
            error_msg = str(e)
            last_error = e
            
            print(f"✗ Failed to load on {attempt_device}: {error_msg[:100]}")
            
            # Check if cuDNN-related error
            if "cudnn" in error_msg.lower():
                print(f"  → cuDNN issue detected. Trying fallback...")
            
            # Continue to next attempt
            continue
    
    # All attempts failed
    raise RuntimeError(
        f"Failed to load Whisper model after {len(load_attempts)} attempts.\n"
        f"Last error: {last_error}\n"
        f"Suggestions:\n"
        f"  1. Install cuDNN: sudo apt-get install libcudnn9\n"
        f"  2. Use CPU mode (slower but works): device='cpu'"
    )


def get_model_info() -> Dict[str, any]:
    """
    Get information about the currently loaded model.
    
    Returns:
        Dictionary with model status and system info
    """
    info = {
        "loaded": model is not None,
        "model_size": current_model_size,
        "device": current_device,
        "system_info": None,
        "cudnn_disabled": not torch.backends.cudnn.enabled
    }
    
    if PLATFORM_UTILS_AVAILABLE:
        info["system_info"] = get_system_info()
    
    return info


def unload_model() -> None:
    """Unload the current model from memory."""
    global model, current_device, current_model_size
    
    if model is not None:
        print("Unloading Whisper model...")
        model = None
        current_device = None
        current_model_size = None
        print("✓ Model unloaded")
    else:
        print("No model loaded")


# ============================================================================
# Transcription Functions
# ============================================================================

def transcribe_audio(
    file_path: str,
    model_size: str = "auto",
    device: str = "auto",
    language: Optional[str] = None,
    task: str = "transcribe",
    beam_size: int = 5,
    best_of: int = 5,
    temperature: float = 0.0
) -> dict:
    """
    Transcribes audio from a file with robust error handling.
    
    Implements automatic fallback strategy if GPU fails.
    
    Args:
        file_path: Path to audio/video file
        model_size: Model size ("auto", "tiny", "base", "small", "medium", "large-v2", "large-v3")
        device: Device ("auto", "cuda", "cpu")
        language: Language code (e.g., "en", "es") or None for auto-detection
        task: "transcribe" or "translate"
        beam_size: Beam size for decoding
        best_of: Number of candidates
        temperature: Sampling temperature
    
    Returns:
        dict: {
            "text": str,
            "segments": [{"id": int, "start": float, "end": float, "text": str}, ...],
            "language": str
        }
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    global model
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")
    
    # Lazy load model if not already loaded
    if model is None:
        try:
            initialize_model(model_size=model_size, device=device)
        except Exception as e:
            print(f"[ERROR] Model initialization failed: {e}")
            raise
    
    print(f"Starting transcription for {file_path}...")
    
    try:
        # Transcribe using faster-whisper
        try:
            segments, info = model.transcribe(
                
            file_path,
            language=language,
            task=task,
            beam_size=beam_size,
            best_of=best_of,
            temperature=temperature,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500
            )
        
            )
        except Exception as e:
            _msg = str(e).lower()
            if 'cudnn' in _msg or 'libcudnn' in _msg:
                print('[GPU] cuDNN-related error detected → retrying on CPU without VAD…')
                initialize_model(model_size=current_model_size or model_size, device='cpu')
                segments, info = model.transcribe(
                    file_path,
                    language=language,
                    task=task,
                    beam_size=beam_size,
                    best_of=best_of,
                    temperature=temperature,
                    vad_filter=False,
                )
            else:
                raise

        
        # Convert segments generator to list
        segments_list = []
        full_text = []
        
        for segment in segments:
            segment_dict = {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            segments_list.append(segment_dict)
            full_text.append(segment.text.strip())
        
        # Build result dictionary
        result = {
            "text": " ".join(full_text),
            "segments": segments_list,
            "language": info.language
        }
        
        print("✓ Transcription completed.")
        print(f"  Language: {info.language}")
        print(f"  Duration: {info.duration:.1f}s")
        print(f"  Segments: {len(segments_list)}")
        
        return result
        
    except Exception as e:
        error_msg = f"An error occurred during transcription: {e}"
        print(f"✗ {error_msg}")
        
        # Return empty result with error
        return {
            "text": "",
            "segments": [],
            "language": "unknown",
            "error": str(e)
        }


# ============================================================================
# Utility Functions
# ============================================================================

def get_supported_formats() -> List[str]:
    """Get list of supported audio/video formats."""
    return [
        ".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus",
        ".mp4", ".mkv", ".avi", ".mov", ".webm"
    ]


def validate_audio_file(file_path: str) -> Tuple[bool, str]:
    """Validate if a file exists and has a supported format."""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    file_ext = Path(file_path).suffix.lower()
    supported = get_supported_formats()
    
    if file_ext not in supported:
        return False, f"Unsupported format: {file_ext}"
    
    return True, "Valid audio file"


# ============================================================================
# Testing / Demo
# ============================================================================

if __name__ == "__main__":
    """Demo/test script for transcription service."""
    print("\n" + "=" * 60)
    print("TRANSCRIPTION SERVICE - DIAGNOSTIC MODE")
    print("=" * 60)
    
    # Print diagnostics
    print_cuda_diagnostics()
    
    # Show model info
    print("\nCURRENT MODEL STATUS")
    print("-" * 60)
    info = get_model_info()
    print(f"Model Loaded: {info['loaded']}")
    print(f"cuDNN Disabled: {info['cudnn_disabled']}")
    print("-" * 60)
    
    # Test transcription if file provided
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"\nTesting transcription: {test_file}")
        print("-" * 60)
        
        is_valid, msg = validate_audio_file(test_file)
        if is_valid:
            try:
                import time
                start = time.time()
                result = transcribe_audio(test_file)
                elapsed = time.time() - start
                
                print(f"\n✅ SUCCESS!")
                print(f"Time: {elapsed:.2f}s")
                print(f"Text: {result['text'][:150]}...")
                print(f"Language: {result['language']}")
            except Exception as e:
                print(f"✗ Failed: {e}")
        else:
            print(f"✗ {msg}")
    else:
        print("\nTo test transcription:")
        print("  python transcription_service.py path/to/audio.mp3")
    
    print("\n" + "=" * 60)
    print("✓ Diagnostic complete")
    print("=" * 60 + "\n")
