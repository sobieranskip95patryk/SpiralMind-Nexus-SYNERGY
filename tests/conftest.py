"""
Pytest configuration and fixtures
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_file(temp_dir):
    """Create sample config file for testing"""
    config_content = """
system:
  version: "0.2.0"
  env: "test"

pipeline:
  mode: "BALANCED"
  max_iterations: 10
  confidence_threshold: 0.75
  success_threshold: 0.85

integrations:
  x_platform: false

logging:
  level: "INFO"
  format: "%(asctime)s %(levelname)s %(name)s :: %(message)s"

quantum:
  max_fibonacci_n: 55
  matrix_weights: [3, 4, 7, 7, 4, 3]
  alpha_schedule: [0.10, 0.20, 0.35, 0.50, 0.35, 0.20, 0.10]
"""
    
    config_path = temp_dir / "test_config.yaml"
    config_path.write_text(config_content.strip())
    return config_path


@pytest.fixture
def sample_batch_file(temp_dir):
    """Create sample batch input file for testing"""
    import json
    
    batch_data = [
        "Simple test input",
        {"text": "Complex input", "context": {"source": "test"}},
        "Another test case with more words and complexity"
    ]
    
    batch_path = temp_dir / "test_batch.json"
    batch_path.write_text(json.dumps(batch_data, indent=2))
    return batch_path


# Test configuration
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )