from dataclasses import dataclass
from typing import Literal, List
import yaml
import pathlib

Mode = Literal["VERIFICATION", "CREATIVE", "BALANCED"]

@dataclass
class PipelineCfg:
    mode: Mode
    max_iterations: int
    confidence_threshold: float
    success_threshold: float

@dataclass
class LoggingCfg:
    level: str
    format: str

@dataclass
class QuantumCfg:
    max_fibonacci_n: int
    matrix_weights: List[int]
    alpha_schedule: List[float]

@dataclass
class IntegrationsCfg:
    x_platform: bool

@dataclass
class Cfg:
    version: str
    env: str
    pipeline: PipelineCfg
    integrations: IntegrationsCfg
    logging: LoggingCfg
    quantum: QuantumCfg

def load_config(path: str = "config/config.yaml") -> Cfg:
    """Load configuration from YAML file with validation"""
    try:
        config_path = pathlib.Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        
        # Extract sections
        system = data.get("system", {})
        pipeline = data.get("pipeline", {})
        integrations = data.get("integrations", {})
        logging_cfg = data.get("logging", {})
        quantum = data.get("quantum", {})
        
        return Cfg(
            version=system.get("version", "0.2.0"),
            env=system.get("env", "development"),
            pipeline=PipelineCfg(
                mode=pipeline.get("mode", "BALANCED"),
                max_iterations=pipeline.get("max_iterations", 100),
                confidence_threshold=pipeline.get("confidence_threshold", 0.75),
                success_threshold=pipeline.get("success_threshold", 0.85),
            ),
            integrations=IntegrationsCfg(
                x_platform=integrations.get("x_platform", False)
            ),
            logging=LoggingCfg(
                level=logging_cfg.get("level", "INFO"),
                format=logging_cfg.get("format", "%(asctime)s %(levelname)s %(name)s :: %(message)s")
            ),
            quantum=QuantumCfg(
                max_fibonacci_n=quantum.get("max_fibonacci_n", 55),
                matrix_weights=quantum.get("matrix_weights", [3, 4, 7, 7, 4, 3]),
                alpha_schedule=quantum.get("alpha_schedule", [0.10, 0.20, 0.35, 0.50, 0.35, 0.20, 0.10])
            )
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {path}: {e}")

def validate_config(cfg: Cfg) -> None:
    """Validate configuration values"""
    if cfg.pipeline.mode not in ["VERIFICATION", "CREATIVE", "BALANCED"]:
        raise ValueError(f"Invalid pipeline mode: {cfg.pipeline.mode}")
    
    if not 0.0 <= cfg.pipeline.confidence_threshold <= 1.0:
        raise ValueError(f"confidence_threshold must be between 0.0 and 1.0: {cfg.pipeline.confidence_threshold}")
    
    if not 0.0 <= cfg.pipeline.success_threshold <= 1.0:
        raise ValueError(f"success_threshold must be between 0.0 and 1.0: {cfg.pipeline.success_threshold}")
    
    if cfg.pipeline.max_iterations <= 0:
        raise ValueError(f"max_iterations must be positive: {cfg.pipeline.max_iterations}")