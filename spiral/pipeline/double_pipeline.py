"""
Double Pipeline - Main execution engine
"""

from typing import Dict, Any, Tuple
import logging
from .synergy_orchestrator import SynergyOrchestrator, OrchestratorResult
from ..config.loader import Cfg


def execute(event: Dict[str, Any], cfg: Cfg) -> Tuple[OrchestratorResult, int]:
    """
    Execute double pipeline processing for an event
    
    Args:
        event: Event dictionary with text and optional context
        cfg: Configuration object
        
    Returns:
        Tuple of (final_result, iterations_used)
    """
    logger = logging.getLogger(__name__)
    
    # Initialize orchestrator with config
    orchestrator = SynergyOrchestrator(
        mode=cfg.pipeline.mode,
        confidence_threshold=cfg.pipeline.confidence_threshold,
        success_threshold=cfg.pipeline.success_threshold,
        max_iterations=cfg.pipeline.max_iterations
    )
    
    logger.info(f"Starting pipeline execution (mode: {cfg.pipeline.mode})")
    
    # Execute with iterative processing
    result = orchestrator.process_iteratively(event)
    
    logger.info(f"Pipeline completed: {result.decision} after {result.iteration} iterations")
    
    return result, result.iteration


def execute_batch(events: list[Dict[str, Any]], cfg: Cfg) -> list[Tuple[OrchestratorResult, int]]:
    """
    Execute batch processing for multiple events
    
    Args:
        events: List of event dictionaries
        cfg: Configuration object
        
    Returns:
        List of (result, iterations) tuples
    """
    results = []
    
    for i, event in enumerate(events):
        logging.info(f"Processing event {i+1}/{len(events)}")
        result = execute(event, cfg)
        results.append(result)
    
    return results


def create_event(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a properly formatted event dictionary
    
    Args:
        text: Input text to process
        context: Optional context information
        
    Returns:
        Event dictionary
    """
    return {
        "text": text,
        "context": context or {}
    }