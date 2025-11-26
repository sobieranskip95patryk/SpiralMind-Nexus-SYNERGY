"""
GOKAI Core - Scoring and calculation engine
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from .quantum_core import text_complexity, quantum_score


@dataclass
class Score:
    """Score result from GOKAI calculations"""
    confidence: float
    success: float
    
    def __post_init__(self):
        """Validate score values"""
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.success = max(0.0, min(1.0, self.success))


class GOKAICalculator:
    """
    Main GOKAI scoring engine with multiple algorithms
    """
    
    def __init__(self, mode: str = "BALANCED"):
        """
        Initialize calculator
        
        Args:
            mode: Calculation mode - VERIFICATION, CREATIVE, or BALANCED
        """
        self.mode = mode
        self.score_weights = self._get_mode_weights(mode)
    
    def _get_mode_weights(self, mode: str) -> Dict[str, float]:
        """Get scoring weights based on mode"""
        weights = {
            "VERIFICATION": {
                "confidence_boost": 0.8,
                "success_penalty": 0.2,
                "complexity_weight": 0.3,
                "entropy_weight": 0.7
            },
            "CREATIVE": {
                "confidence_boost": 0.2,
                "success_penalty": 0.8,
                "complexity_weight": 0.7,
                "entropy_weight": 0.3
            },
            "BALANCED": {
                "confidence_boost": 0.5,
                "success_penalty": 0.5,
                "complexity_weight": 0.5,
                "entropy_weight": 0.5
            }
        }
        return weights.get(mode, weights["BALANCED"])
    
    def score_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> Score:
        """
        Score text using GOKAI algorithm
        
        Args:
            text: Input text to score
            context: Optional context information
            
        Returns:
            Score object with confidence and success values
        """
        if not text:
            return Score(confidence=0.0, success=0.0)
        
        # Get basic complexity metrics
        complexity_metrics = text_complexity(text)
        quantum_metrics = quantum_score(text)
        
        # Calculate base confidence from vocabulary diversity
        vocab_diversity = (complexity_metrics["vocab"] / 
                          (complexity_metrics["len_words"] + 1e-9))
        
        base_confidence = min(0.99, 0.4 + 0.6 * vocab_diversity)
        
        # Calculate base success from entropy
        entropy_normalized = min(1.0, complexity_metrics["entropy"] / 5.0)
        base_success = min(0.99, 0.3 + 0.7 * entropy_normalized)
        
        # Apply mode-specific adjustments
        weights = self.score_weights
        
        confidence = base_confidence * weights["confidence_boost"]
        success = base_success * (1.0 - weights["success_penalty"])
        
        # Apply complexity and entropy weights
        complexity_factor = complexity_metrics["complexity_score"] * weights["complexity_weight"]
        entropy_factor = entropy_normalized * weights["entropy_weight"]
        
        # Final scoring with quantum component
        quantum_boost = quantum_metrics["quantum_score"] * 0.1
        
        final_confidence = min(0.99, confidence + complexity_factor + quantum_boost)
        final_success = min(0.99, success + entropy_factor + quantum_boost)
        
        # Apply context adjustments if provided
        if context:
            final_confidence, final_success = self._apply_context_adjustments(
                final_confidence, final_success, context
            )
        
        return Score(confidence=final_confidence, success=final_success)
    
    def _apply_context_adjustments(self, confidence: float, success: float, 
                                 context: Dict[str, Any]) -> tuple[float, float]:
        """Apply context-based adjustments to scores"""
        
        # X Platform boost
        if context.get("source") == "x_platform":
            confidence *= 1.1
            success *= 1.05
        
        # Media type adjustments
        media_type = context.get("media_type", "text")
        if media_type == "image":
            success *= 1.2
        elif media_type == "video":
            success *= 1.3
        
        # Leadership content penalty (requires verification)
        if any(leader in context.get("text", "").lower() 
               for leader in ["ceo", "leader", "executive"]):
            confidence *= 0.9
        
        return confidence, success
    
    def batch_score(self, texts: list[str], 
                   contexts: Optional[list[Dict[str, Any]]] = None) -> list[Score]:
        """
        Score multiple texts in batch
        
        Args:
            texts: List of texts to score
            contexts: Optional list of context dictionaries
            
        Returns:
            List of Score objects
        """
        if contexts is None:
            contexts = [None] * len(texts)
        
        return [self.score_text(text, context) 
                for text, context in zip(texts, contexts)]
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get information about current mode"""
        return {
            "mode": self.mode,
            "weights": self.score_weights,
            "description": {
                "VERIFICATION": "Prioritizes accuracy and confidence",
                "CREATIVE": "Encourages innovation and complexity", 
                "BALANCED": "Balances verification and creativity"
            }.get(self.mode, "Unknown mode")
        }