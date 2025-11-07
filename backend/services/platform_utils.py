"""
Platform and GPU Detection Utility Module

This module provides cross-platform detection capabilities for:
- Operating system identification (Windows, macOS, Linux)
- GPU type detection (CUDA, Metal, CPU)
- Compute device selection for ML models
- System information gathering

Version: 1.0 - Cross-Platform Support
Author: InsightsLM Development Team
Date: November 6, 2025
"""

import platform
import sys
from typing import Dict, Optional

# Try importing torch for GPU detection
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[WARNING] PyTorch not available - GPU detection disabled")

# Try importing cpuinfo for CPU details
try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False
    print("[INFO] py-cpuinfo not available - limited CPU info")


# ============================================================================
# Platform Detection
# ============================================================================

def get_platform() -> str:
    """
    Detects the current operating system platform.
    
    Returns:
        str: Platform identifier - one of:
            - 'windows': Windows OS (any version)
            - 'macos': macOS / Mac OS X
            - 'linux': Linux distributions
            - 'unknown': Unable to determine platform
    
    Examples:
        >>> get_platform()
        'windows'  # On Windows
        'macos'    # On macOS
        'linux'    # On Linux/WSL
    """
    system = platform.system().lower()
    
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        print(f"[WARNING] Unknown platform: {system}")
        return 'unknown'


def get_platform_info() -> Dict[str, str]:
    """
    Gathers detailed platform information.
    
    Returns:
        dict: Platform details including:
            - platform: OS identifier (windows/macos/linux)
            - system: System name from platform.system()
            - release: OS release version
            - version: Detailed OS version
            - machine: Machine type (x86_64, arm64, etc.)
            - processor: Processor name
            - python_version: Python interpreter version
    
    Example:
        >>> get_platform_info()
        {
            'platform': 'windows',
            'system': 'Windows',
            'release': '10',
            'version': '10.0.19045',
            'machine': 'AMD64',
            'processor': 'Intel64 Family 6 Model 141 Stepping 1, GenuineIntel',
            'python_version': '3.12.3'
        }
    """
    return {
        'platform': get_platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }


# ============================================================================
# GPU Detection
# ============================================================================

def has_cuda() -> bool:
    """
    Checks if CUDA (NVIDIA GPU) is available.
    
    Returns:
        bool: True if CUDA-capable GPU is detected and available
    
    Notes:
        - Requires PyTorch with CUDA support installed
        - Returns False if PyTorch is not available
        - Windows/Linux: NVIDIA GPUs with CUDA drivers
    """
    if not TORCH_AVAILABLE:
        return False
    
    try:
        return torch.cuda.is_available()
    except Exception as e:
        print(f"[WARNING] Error checking CUDA availability: {e}")
        return False


def has_metal() -> bool:
    """
    Checks if Metal (Apple Silicon GPU) is available.
    
    Returns:
        bool: True if Metal Performance Shaders (MPS) backend is available
    
    Notes:
        - Only available on macOS with Apple Silicon (M1/M2/M3)
        - Requires PyTorch 1.12+ with MPS support
        - Returns False on Intel Macs
    """
    if not TORCH_AVAILABLE:
        return False
    
    if get_platform() != 'macos':
        return False
    
    try:
        # Check if MPS backend is available (PyTorch 1.12+)
        return torch.backends.mps.is_available()
    except AttributeError:
        # Older PyTorch version without MPS support
        return False
    except Exception as e:
        print(f"[WARNING] Error checking Metal availability: {e}")
        return False


def get_gpu_type() -> str:
    """
    Detects the type of GPU acceleration available.
    
    Returns:
        str: GPU type identifier - one of:
            - 'cuda': NVIDIA GPU with CUDA support (Windows/Linux)
            - 'metal': Apple Silicon with Metal support (macOS)
            - 'cpu': No GPU acceleration available (fallback)
    
    Detection Priority:
        1. CUDA (if available on any platform)
        2. Metal (if on macOS with Apple Silicon)
        3. CPU (fallback)
    
    Examples:
        >>> get_gpu_type()
        'cuda'   # On Windows/Linux with NVIDIA GPU
        'metal'  # On macOS with Apple Silicon
        'cpu'    # On any system without GPU
    """
    # Priority 1: Check for CUDA (works on Windows and Linux)
    if has_cuda():
        return 'cuda'
    
    # Priority 2: Check for Metal (macOS only)
    if has_metal():
        return 'metal'
    
    # Fallback: CPU only
    return 'cpu'


def get_compute_device() -> str:
    """
    Returns the appropriate device string for PyTorch/ML model loading.
    
    Returns:
        str: PyTorch device string - one of:
            - 'cuda': For NVIDIA GPUs
            - 'mps': For Apple Metal (macOS)
            - 'cpu': For CPU-only computation
    
    Usage Example:
        >>> device = get_compute_device()
        >>> model = WhisperModel("large-v3", device=device)
    
    Notes:
        - This string can be used directly in PyTorch model loading
        - Metal uses 'mps' (Metal Performance Shaders) as device name
        - Automatically selects best available option
    """
    gpu_type = get_gpu_type()
    
    if gpu_type == 'cuda':
        return 'cuda'
    elif gpu_type == 'metal':
        return 'mps'  # Metal Performance Shaders
    else:
        return 'cpu'


def get_cuda_device_name() -> Optional[str]:
    """
    Gets the name of the CUDA GPU if available.
    
    Returns:
        Optional[str]: GPU name (e.g., "NVIDIA GeForce RTX 3080") or None
    
    Examples:
        >>> get_cuda_device_name()
        'NVIDIA GeForce RTX 3080'  # On Windows/Linux with NVIDIA GPU
        None                        # On systems without CUDA
    """
    if not has_cuda():
        return None
    
    try:
        return torch.cuda.get_device_name(0)
    except Exception as e:
        print(f"[WARNING] Error getting CUDA device name: {e}")
        return None


def get_cuda_memory_info() -> Optional[Dict[str, int]]:
    """
    Gets CUDA GPU memory information.
    
    Returns:
        Optional[Dict[str, int]]: Memory info in bytes, or None if not available
            - total: Total GPU memory
            - allocated: Currently allocated memory
            - reserved: Reserved memory
            - free: Free memory (computed)
    
    Examples:
        >>> get_cuda_memory_info()
        {
            'total': 10737418240,      # 10 GB
            'allocated': 2147483648,    # 2 GB
            'reserved': 2684354560,     # 2.5 GB
            'free': 8589934592          # 8 GB
        }
    """
    if not has_cuda():
        return None
    
    try:
        # Get memory info for device 0
        total = torch.cuda.get_device_properties(0).total_memory
        allocated = torch.cuda.memory_allocated(0)
        reserved = torch.cuda.memory_reserved(0)
        free = total - reserved
        
        return {
            'total': total,
            'allocated': allocated,
            'reserved': reserved,
            'free': free
        }
    except Exception as e:
        print(f"[WARNING] Error getting CUDA memory info: {e}")
        return None


# ============================================================================
# CPU Detection
# ============================================================================

def get_cpu_info() -> Dict[str, any]:
    """
    Gets CPU information.
    
    Returns:
        dict: CPU details including:
            - brand: CPU brand/model name
            - count: Number of logical CPU cores
            - physical_cores: Number of physical CPU cores (if available)
    
    Examples:
        >>> get_cpu_info()
        {
            'brand': 'Intel(R) Core(TM) i7-11800H @ 2.30GHz',
            'count': 16,
            'physical_cores': 8
        }
    """
    import os
    
    cpu_data = {
        'count': os.cpu_count() or 1
    }
    
    # Try to get detailed CPU info if cpuinfo is available
    if CPUINFO_AVAILABLE:
        try:
            info = cpuinfo.get_cpu_info()
            cpu_data['brand'] = info.get('brand_raw', 'Unknown')
            
            # Try to get physical core count
            if 'count' in info:
                cpu_data['physical_cores'] = info['count']
            
        except Exception as e:
            print(f"[WARNING] Error getting detailed CPU info: {e}")
            cpu_data['brand'] = platform.processor()
    else:
        cpu_data['brand'] = platform.processor()
    
    return cpu_data


# ============================================================================
# Comprehensive System Information
# ============================================================================

def get_system_info() -> Dict[str, any]:
    """
    Gathers comprehensive system information including platform, GPU, and CPU.
    
    Returns:
        dict: Complete system information with nested dictionaries:
            - platform: Platform details (from get_platform_info())
            - gpu: GPU information
                - type: 'cuda', 'metal', or 'cpu'
                - device: PyTorch device string
                - available: Boolean indicating GPU availability
                - name: GPU name (if available)
                - memory: GPU memory info (if CUDA)
            - cpu: CPU information (from get_cpu_info())
            - acceleration: Human-readable acceleration description
    
    Example Output:
        >>> get_system_info()
        {
            'platform': {
                'platform': 'windows',
                'system': 'Windows',
                'release': '10',
                'machine': 'AMD64',
                ...
            },
            'gpu': {
                'type': 'cuda',
                'device': 'cuda',
                'available': True,
                'name': 'NVIDIA GeForce RTX 3080',
                'memory': {
                    'total': 10737418240,
                    'allocated': 0,
                    'reserved': 0,
                    'free': 10737418240
                }
            },
            'cpu': {
                'brand': 'Intel(R) Core(TM) i7-11800H',
                'count': 16,
                'physical_cores': 8
            },
            'acceleration': 'NVIDIA CUDA GPU'
        }
    """
    gpu_type = get_gpu_type()
    gpu_info = {
        'type': gpu_type,
        'device': get_compute_device(),
        'available': gpu_type != 'cpu'
    }
    
    # Add GPU-specific details
    if gpu_type == 'cuda':
        gpu_info['name'] = get_cuda_device_name()
        gpu_info['memory'] = get_cuda_memory_info()
    elif gpu_type == 'metal':
        gpu_info['name'] = 'Apple Silicon (Metal)'
        gpu_info['memory'] = None  # Metal doesn't expose memory stats easily
    else:
        gpu_info['name'] = None
        gpu_info['memory'] = None
    
    # Determine acceleration description
    if gpu_type == 'cuda':
        acceleration = f"NVIDIA CUDA GPU ({gpu_info['name']})"
    elif gpu_type == 'metal':
        acceleration = "Apple Silicon Metal GPU"
    else:
        acceleration = "CPU Only (No GPU Acceleration)"
    
    return {
        'platform': get_platform_info(),
        'gpu': gpu_info,
        'cpu': get_cpu_info(),
        'acceleration': acceleration
    }


def print_system_info():
    """
    Prints formatted system information to console.
    
    This function displays a user-friendly summary of the system configuration,
    including platform, GPU capabilities, and CPU information.
    
    Example Output:
        ========================================
        System Information
        ========================================
        Platform: Windows 10 (AMD64)
        Python: 3.12.3
        
        GPU Acceleration: NVIDIA CUDA GPU
        Device: cuda
        GPU: NVIDIA GeForce RTX 3080
        GPU Memory: 10.0 GB total, 10.0 GB free
        
        CPU: Intel(R) Core(TM) i7-11800H @ 2.30GHz
        Cores: 16 logical, 8 physical
        ========================================
    """
    info = get_system_info()
    
    print("=" * 60)
    print("SYSTEM INFORMATION")
    print("=" * 60)
    
    # Platform info
    plat = info['platform']
    print(f"Platform: {plat['system']} {plat['release']} ({plat['machine']})")
    print(f"Python: {plat['python_version']}")
    print()
    
    # GPU info
    gpu = info['gpu']
    print(f"GPU Acceleration: {info['acceleration']}")
    print(f"Device: {gpu['device']}")
    
    if gpu['name']:
        print(f"GPU: {gpu['name']}")
    
    if gpu['memory']:
        mem = gpu['memory']
        total_gb = mem['total'] / (1024**3)
        free_gb = mem['free'] / (1024**3)
        print(f"GPU Memory: {total_gb:.1f} GB total, {free_gb:.1f} GB free")
    
    print()
    
    # CPU info
    cpu = info['cpu']
    print(f"CPU: {cpu['brand']}")
    if 'physical_cores' in cpu:
        print(f"Cores: {cpu['count']} logical, {cpu['physical_cores']} physical")
    else:
        print(f"Cores: {cpu['count']}")
    
    print("=" * 60)


# ============================================================================
# Performance Estimation
# ============================================================================

def estimate_transcription_speed() -> Dict[str, any]:
    """
    Estimates expected transcription speed based on available hardware.
    
    Returns:
        dict: Speed estimates including:
            - hardware: Hardware type (cuda/metal/cpu)
            - speed_factor: Speed relative to real-time (e.g., 30x)
            - description: Human-readable speed description
            - recommendation: Usage recommendation
    
    Examples:
        >>> estimate_transcription_speed()
        {
            'hardware': 'cuda',
            'speed_factor': 30,
            'description': '30x faster than real-time',
            'recommendation': 'Excellent performance with GPU acceleration'
        }
    """
    gpu_type = get_gpu_type()
    
    if gpu_type == 'cuda':
        return {
            'hardware': 'cuda',
            'speed_factor': 30,
            'description': '30x faster than real-time',
            'recommendation': 'Excellent performance with NVIDIA GPU acceleration'
        }
    elif gpu_type == 'metal':
        return {
            'hardware': 'metal',
            'speed_factor': 20,  # Metal typically slightly slower than CUDA
            'description': '20x faster than real-time',
            'recommendation': 'Excellent performance with Apple Silicon GPU'
        }
    else:
        return {
            'hardware': 'cpu',
            'speed_factor': 1,
            'description': 'Real-time (1x) speed',
            'recommendation': 'Consider using smaller model or enable GPU for better performance'
        }


# ============================================================================
# Testing / Demo
# ============================================================================

if __name__ == "__main__":
    """
    Demo/test script showing platform_utils capabilities.
    Run this file directly to see system information.
    
    Usage:
        python platform_utils.py
    """
    print("\n" + "=" * 60)
    print("PLATFORM UTILITIES - DEMONSTRATION")
    print("=" * 60 + "\n")
    
    # Show system info
    print_system_info()
    
    print()
    
    # Show transcription speed estimate
    speed = estimate_transcription_speed()
    print("TRANSCRIPTION PERFORMANCE ESTIMATE")
    print("=" * 60)
    print(f"Hardware: {speed['hardware'].upper()}")
    print(f"Expected Speed: {speed['description']}")
    print(f"Performance: {speed['recommendation']}")
    print("=" * 60)
    
    print()
    
    # Show raw detection results
    print("RAW DETECTION RESULTS")
    print("=" * 60)
    print(f"Platform: {get_platform()}")
    print(f"GPU Type: {get_gpu_type()}")
    print(f"Compute Device: {get_compute_device()}")
    print(f"Has CUDA: {has_cuda()}")
    print(f"Has Metal: {has_metal()}")
    print(f"PyTorch Available: {TORCH_AVAILABLE}")
    print("=" * 60)
    
    print("\n✓ Platform utilities test complete\n")
