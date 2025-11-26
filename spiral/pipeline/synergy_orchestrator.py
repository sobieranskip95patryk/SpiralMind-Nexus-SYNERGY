"""
Synergy Orchestrator - Decision engine for pipeline routing
"""

from dataclasses import dataclass
from typing import Dict, Any
import logging
from ..core.gokai_core import GOKAICalculator, Score


@dataclass
class OrchestratorResult:
    """Result from orchestrator decision process"""
    score: Score
    decision: str
    pipeline_mode: str
    iteration: int
    metadata: Dict[str, Any]


class SynergyOrchestrator:
    """
    Modular orchestrator for intelligent pipeline routing and decision making
    """
    
    def __init__(self, mode: str, confidence_threshold: float, 
                 success_threshold: float, max_iterations: int = 100):
        """
        Initialize orchestrator
        
        Args:
            mode: Pipeline mode (VERIFICATION, CREATIVE, BALANCED)
            confidence_threshold: Minimum confidence for acceptance
            success_threshold: Minimum success rate for acceptance  
            max_iterations: Maximum iterations before forced acceptance
        """
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self.success_threshold = success_threshold
        self.max_iterations = max_iterations
        
        # Initialize calculator with mode
        self.calculator = GOKAICalculator(mode)
        
        # Decision statistics
        self.stats = {
            "total_decisions": 0,
            "accepted": 0,
            "revised": 0,
            "forced_accepted": 0,
            "mode_usage": {mode: 0 for mode in ["VERIFICATION", "CREATIVE", "BALANCED"]}
        }
        
        self.logger = logging.getLogger(__name__)
    
    def run(self, event: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute orchestration decision for an event
        
        Args:
            event: Event dictionary containing 'text' and optional context
            
        Returns:
            OrchestratorResult with decision and metadata
        """
        text = event.get("text", "")
        context = event.get("context", {})
        
        # Initial scoring
        score = self.calculator.score_text(text, context)
        
        # Decision logic
        decision = self._make_decision(score, context)
        pipeline_mode = self._determine_pipeline_mode(score, context)
        
        # Update statistics
        self._update_stats(decision)
        
        # Prepare metadata
        metadata = {
            "original_mode": self.mode,
            "context_applied": bool(context),
            "thresholds": {
                "confidence": self.confidence_threshold,
                "success": self.success_threshold
            },
            "calculator_info": self.calculator.get_mode_info()
        }
        
        result = OrchestratorResult(
            score=score,
            decision=decision,
            pipeline_mode=pipeline_mode,
            iteration=1,
            metadata=metadata
        )
        
        self.logger.info(f"Orchestrator decision: {decision} (mode: {pipeline_mode}, "
                        f"confidence: {score.confidence:.3f}, success: {score.success:.3f})")
        
        return result
    
    def _make_decision(self, score: Score, context: Dict[str, Any]) -> str:
        """Make accept/revise decision based on score and context"""
        
        # Check thresholds
        confidence_ok = score.confidence >= self.confidence_threshold
        success_ok = score.success >= self.success_threshold
        
        # Special handling for X Platform content
        if context.get("source") == "x_platform":
            # Lower thresholds for X content to encourage processing
            confidence_ok = score.confidence >= (self.confidence_threshold * 0.8)
            success_ok = score.success >= (self.success_threshold * 0.8)
        
        # Leadership content requires higher confidence
        if self._is_leadership_content(context):
            confidence_ok = score.confidence >= (self.confidence_threshold * 1.2)
        
        if confidence_ok and success_ok:
            return "ACCEPT"
        else:
            return "REVISE"
    
    def _determine_pipeline_mode(self, score: Score, context: Dict[str, Any]) -> str:
        """Determine which pipeline mode to use"""
        
        # Start with configured mode
        pipeline_mode = self.mode
        
        # Override based on content analysis
        if context.get("media_type") in ["video", "image"]:
            # Media content benefits from creative processing
            pipeline_mode = "CREATIVE"
            
        elif self._is_leadership_content(context):
            # Leadership content needs verification
            pipeline_mode = "VERIFICATION"
            
        elif score.confidence < 0.5:
            # Low confidence -> verification mode
            pipeline_mode = "VERIFICATION"
            
        elif score.success > 0.8 and "creative" in context.get("text", "").lower():
            # High success + creative keywords -> creative mode  
            pipeline_mode = "CREATIVE"
        
        return pipeline_mode
    
    def _is_leadership_content(self, context: Dict[str, Any]) -> bool:
        """Check if content is leadership-related"""
        text = context.get("text", "").lower()
        leadership_keywords = ["ceo", "leader", "executive", "manager", "director"]
        return any(keyword in text for keyword in leadership_keywords)
    
    def _update_stats(self, decision: str):
        """Update decision statistics"""
        self.stats["total_decisions"] += 1
        
        if decision == "ACCEPT":
            self.stats["accepted"] += 1
        else:
            self.stats["revised"] += 1
        
        self.stats["mode_usage"][self.mode] += 1
    
    def process_iteratively(self, event: Dict[str, Any]) -> OrchestratorResult:
        """
        Process event with iterative refinement
        
        Args:
            event: Event to process
            
        Returns:
            Final orchestrator result
        """
        iteration = 0
        current_event = event.copy()
        
        while iteration < self.max_iterations:
            iteration += 1
            result = self.run(current_event)
            
            if result.decision == "ACCEPT":
                result.iteration = iteration
                return result
            
            # Refine event for next iteration
            current_event = self._refine_event(current_event, result)
        
        # Force acceptance after max iterations
        self.stats["forced_accepted"] += 1
        result.decision = "FORCE_ACCEPT"
        result.iteration = iteration
        
        self.logger.warning(f"Forced acceptance after {iteration} iterations")
        return result
    
    def _refine_event(self, event: Dict[str, Any], result: OrchestratorResult) -> Dict[str, Any]:
        """
        Refine event based on previous result
        This could involve text preprocessing, context enhancement, etc.
        """
        refined_event = event.copy()
        
        # Simple refinement: add metadata about previous iteration
        if "refinement_history" not in refined_event:
            refined_event["refinement_history"] = []
        
        refined_event["refinement_history"].append({
            "iteration": result.iteration,
            "score": {
                "confidence": result.score.confidence,
                "success": result.score.success
            },
            "decision": result.decision
        })
        
        return refined_event
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator performance statistics"""
        total = self.stats["total_decisions"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "acceptance_rate": self.stats["accepted"] / total,
            "revision_rate": self.stats["revised"] / total,
            "force_acceptance_rate": self.stats["forced_accepted"] / total
        }
    
    def reset_statistics(self):
        """Reset all statistics"""
        for key in self.stats:
            if isinstance(self.stats[key], dict):
                for subkey in self.stats[key]:
                    self.stats[key][subkey] = 0
            else:
                self.stats[key] = 0