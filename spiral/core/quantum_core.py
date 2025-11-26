"""
Quantum Core - Fibonacci sequences, entropy calculations, and text complexity metrics
"""

import math
from collections import Counter
from typing import Dict, Any


def fib(n: int) -> int:
    """
    Calculate Fibonacci number for position n
    
    Args:
        n: Position in Fibonacci sequence (must be >= 0)
        
    Returns:
        Fibonacci number at position n
        
    Raises:
        ValueError: If n < 0
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def shannon_entropy(text: str) -> float:
    """
    Calculate Shannon entropy for text
    
    Args:
        text: Input text to analyze
        
    Returns:
        Shannon entropy value (0.0 for empty text)
    """
    if not text:
        return 0.0
    
    counts = Counter(text)
    total = len(text)
    
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            probability = count / total
            entropy -= probability * math.log2(probability)
    
    return entropy


def text_complexity(text: str) -> Dict[str, Any]:
    """
    Calculate comprehensive text complexity metrics
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with complexity metrics:
        - len_chars: Character count
        - len_words: Word count  
        - vocab: Unique word count
        - entropy: Shannon entropy
        - avg_word_len: Average word length
        - complexity_score: Normalized complexity (0.0-1.0)
    """
    if not text:
        return {
            "len_chars": 0,
            "len_words": 0,
            "vocab": 0,
            "entropy": 0.0,
            "avg_word_len": 0.0,
            "complexity_score": 0.0
        }
    
    # Basic metrics
    words = [w for w in text.split() if w.strip()]
    chars = len(text)
    vocab = len(set(words))
    entropy = shannon_entropy(text)
    
    # Average word length
    avg_word_len = (sum(map(len, words)) / len(words)) if words else 0.0
    
    # Complexity score (normalized 0.0-1.0)
    # Based on entropy, vocabulary diversity, and structure
    vocab_diversity = (vocab / len(words)) if words else 0.0
    entropy_normalized = min(1.0, entropy / 5.0)  # Normalize entropy to 0-1 range
    
    complexity_score = min(1.0, (
        entropy_normalized * 0.4 +
        vocab_diversity * 0.3 +
        min(1.0, avg_word_len / 10.0) * 0.2 +
        min(1.0, len(words) / 100.0) * 0.1
    ))
    
    return {
        "len_chars": chars,
        "len_words": len(words),
        "vocab": vocab,
        "entropy": entropy,
        "avg_word_len": avg_word_len,
        "complexity_score": complexity_score
    }


def apply_formula_S(n: int, params: Dict[str, int]) -> Dict[str, float]:
    """
    Apply the GOKAI S formula: S = S9 * π + F(n)
    
    Args:
        n: Fibonacci sequence position
        params: Parameter dictionary with W, M, D, C, A, E, T values
        
    Returns:
        Dictionary with S9, S_pi, Fn, and WYNIK values
    """
    # Calculate S9 (sum of params reduced to single digit)
    param_sum = sum(params.values())
    S9 = param_sum % 9 or 9  # Reduce to 1-9 range
    
    # Calculate components
    S_pi = S9 * math.pi
    Fn = fib(n)
    wynik = S_pi + Fn
    
    return {
        "S9": S9,
        "S_pi": S_pi,
        "Fn": Fn,
        "WYNIK": wynik
    }


def quantum_score(text: str, fibonacci_n: int = 9) -> Dict[str, float]:
    """
    Calculate quantum-inspired scoring for text
    
    Args:
        text: Input text
        fibonacci_n: Fibonacci sequence position to use
        
    Returns:
        Dictionary with quantum metrics
    """
    # Handle empty text explicitly
    if not text.strip():
        return {
            "quantum_score": 0.0,
            "text_complexity": 0.0,
            "entropy": 0.0,
            "s_formula_result": 0.0,
            "fibonacci_component": 0
        }
    
    complexity = text_complexity(text)
    
    # Default GOKAI parameters
    default_params = {
        "W": 7, "M": 6, "D": 4, "C": 5, 
        "A": 8, "E": 6, "T": 3
    }
    
    s_formula = apply_formula_S(fibonacci_n, default_params)
    
    # Combine complexity with quantum formula
    quantum_score_value = min(1.0, (
        complexity["complexity_score"] * 0.6 +
        (s_formula["WYNIK"] / 100.0) * 0.4
    ))
    
    return {
        "quantum_score": quantum_score_value,
        "text_complexity": complexity["complexity_score"],
        "entropy": complexity["entropy"],
        "s_formula_result": s_formula["WYNIK"],
        "fibonacci_component": s_formula["Fn"]
    }