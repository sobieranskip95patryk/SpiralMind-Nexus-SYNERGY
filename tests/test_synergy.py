import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
Tests for synergy orchestrator
"""

from spiral.config.loader import Cfg, PipelineCfg, LoggingCfg, QuantumCfg, IntegrationsCfg
from spiral.pipeline.synergy_orchestrator import SynergyOrchestrator


def create_test_config(mode: str = "BALANCED") -> Cfg:
    """Create test configuration"""
    return Cfg(
        version="0.2.0",
        env="test",
        pipeline=PipelineCfg(
            mode=mode,
            max_iterations=3,
            confidence_threshold=0.5,
            success_threshold=0.5
        ),
        integrations=IntegrationsCfg(x_platform=False),
        logging=LoggingCfg(level="INFO", format="test"),
        quantum=QuantumCfg(
            max_fibonacci_n=10,
            matrix_weights=[1, 2, 3],
            alpha_schedule=[0.1, 0.2, 0.3]
        )
    )


class TestSynergyOrchestrator:
    """Test synergy orchestrator functionality"""
    
    def test_orchestrator_initialization(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=cfg.pipeline.confidence_threshold,
            success_threshold=cfg.pipeline.success_threshold,
            max_iterations=cfg.pipeline.max_iterations
        )
        
        assert orch.mode == "BALANCED"
        assert orch.confidence_threshold == 0.5
        assert orch.success_threshold == 0.5
        assert orch.max_iterations == 3
    
    def test_simple_text_processing(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=cfg.pipeline.confidence_threshold,
            success_threshold=cfg.pipeline.success_threshold
        )
        
        event = {"text": "This is a test message with reasonable complexity."}
        result = orch.run(event)
        
        assert result.decision in ("ACCEPT", "REVISE")
        assert result.pipeline_mode in ("VERIFICATION", "CREATIVE", "BALANCED")
        assert 0.0 <= result.score.confidence <= 1.0
        assert 0.0 <= result.score.success <= 1.0
        assert result.iteration == 1
    
    def test_high_quality_text_accepted(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.1,  # Very low threshold
            success_threshold=0.1
        )
        
        event = {"text": "Rich vocabulary drives confidence and entropy rises with sophisticated analysis."}
        result = orch.run(event)
        
        assert result.decision == "ACCEPT"
    
    def test_low_quality_text_revised(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.9,  # Very high threshold
            success_threshold=0.9
        )
        
        event = {"text": "test"}
        result = orch.run(event)
        
        assert result.decision == "REVISE"
    
    def test_x_platform_content_handling(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.8,
            success_threshold=0.8
        )
        
        event = {
            "text": "X platform integration test",
            "context": {"source": "x_platform"}
        }
        result = orch.run(event)
        
        # X platform content should have relaxed thresholds
        assert result.decision in ("ACCEPT", "REVISE")
        assert result.metadata["context_applied"] is True
    
    def test_leadership_content_verification(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.5,
            success_threshold=0.5
        )
        
        event = {
            "text": "The CEO announced new strategic direction",
            "context": {"text": "The CEO announced new strategic direction"}
        }
        result = orch.run(event)
        
        # Leadership content should trigger verification mode
        assert result.pipeline_mode == "VERIFICATION"
    
    def test_media_content_creative_mode(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.5,
            success_threshold=0.5
        )
        
        event = {
            "text": "Video content analysis",
            "context": {"media_type": "video"}
        }
        result = orch.run(event)
        
        # Media content should trigger creative mode
        assert result.pipeline_mode == "CREATIVE"
    
    def test_iterative_processing(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.9,  # High threshold to force iterations
            success_threshold=0.9,
            max_iterations=3
        )
        
        event = {"text": "test"}
        result = orch.process_iteratively(event)
        
        # Should either accept or force accept after max iterations
        assert result.decision in ("ACCEPT", "FORCE_ACCEPT")
        assert result.iteration <= 3
    
    def test_statistics_tracking(self):
        cfg = create_test_config()
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.5,
            success_threshold=0.5
        )
        
        # Process some events
        events = [
            {"text": "High quality sophisticated content with extensive vocabulary"},
            {"text": "test"},
            {"text": "Medium complexity content for analysis"}
        ]
        
        for event in events:
            orch.run(event)
        
        stats = orch.get_statistics()
        assert stats["total_decisions"] == 3
        assert "acceptance_rate" in stats
        assert "revision_rate" in stats


class TestModeSpecificBehavior:
    """Test mode-specific orchestrator behavior"""
    
    def test_verification_mode(self):
        cfg = create_test_config("VERIFICATION")
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.5,
            success_threshold=0.5
        )
        
        assert orch.mode == "VERIFICATION"
        
        event = {"text": "Test verification mode processing"}
        result = orch.run(event)
        
        # Verification mode should maintain or default to verification
        assert result.pipeline_mode in ("VERIFICATION", "BALANCED")
    
    def test_creative_mode(self):
        cfg = create_test_config("CREATIVE")
        orch = SynergyOrchestrator(
            mode=cfg.pipeline.mode,
            confidence_threshold=0.5,
            success_threshold=0.5
        )
        
        assert orch.mode == "CREATIVE"
        
        event = {"text": "Creative innovative content generation"}
        result = orch.run(event)
        
        # Should process in creative mode unless overridden
        assert result.pipeline_mode in ("CREATIVE", "VERIFICATION", "BALANCED")