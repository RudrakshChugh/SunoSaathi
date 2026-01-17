"""
Shared utility functions
"""
import logging
import time
from functools import wraps
from typing import Any, Callable
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

def timing_decorator(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger = get_logger(func.__module__)
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger = get_logger(func.__module__)
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def normalize_keypoints(keypoints: np.ndarray) -> np.ndarray:
    """
    Normalize keypoints to [-1, 1] range
    
    Args:
        keypoints: Array of shape (num_frames, num_keypoints, 3)
    
    Returns:
        Normalized keypoints
    """
    # Center around origin
    mean = np.mean(keypoints, axis=(0, 1), keepdims=True)
    centered = keypoints - mean
    
    # Scale to [-1, 1]
    max_val = np.max(np.abs(centered))
    if max_val > 0:
        normalized = centered / max_val
    else:
        normalized = centered
    
    return normalized

def pad_sequence(sequence: np.ndarray, max_length: int, padding_value: float = 0.0) -> np.ndarray:
    """
    Pad sequence to max_length
    
    Args:
        sequence: Array of shape (seq_len, features)
        max_length: Target sequence length
        padding_value: Value to use for padding
    
    Returns:
        Padded sequence of shape (max_length, features)
    """
    seq_len = sequence.shape[0]
    
    if seq_len >= max_length:
        return sequence[:max_length]
    
    pad_length = max_length - seq_len
    padding = np.full((pad_length, *sequence.shape[1:]), padding_value)
    
    return np.concatenate([sequence, padding], axis=0)

import asyncio
