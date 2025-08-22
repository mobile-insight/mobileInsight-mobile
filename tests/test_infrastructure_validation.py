"""Validation tests to verify the testing infrastructure is properly set up."""

import os
import sys
import tempfile
from pathlib import Path
import pytest
from unittest.mock import Mock


class TestInfrastructureValidation:
    """Test class to validate the testing infrastructure setup."""
    
    def test_python_path_configured(self):
        """Test that the Python path includes the project root."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assert project_root in sys.path, "Project root should be in Python path"
    
    def test_temp_dir_fixture(self, temp_dir):
        """Test the temp_dir fixture creates and cleans up properly."""
        assert temp_dir.exists(), "Temporary directory should exist"
        assert temp_dir.is_dir(), "Should be a directory"
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists(), "Should be able to create files in temp dir"
    
    def test_temp_file_fixture(self, temp_file):
        """Test the temp_file fixture creates a file with content."""
        assert temp_file.exists(), "Temporary file should exist"
        assert temp_file.is_file(), "Should be a file"
        assert temp_file.read_text() == "test content", "File should contain test content"
    
    def test_mock_config_fixture(self, mock_config):
        """Test the mock_config fixture provides expected configuration."""
        assert isinstance(mock_config, dict), "Config should be a dictionary"
        assert "debug" in mock_config, "Config should have debug setting"
        assert "plugins" in mock_config, "Config should have plugins section"
        assert mock_config["plugins"]["enabled"] is True, "Plugins should be enabled in test config"
    
    def test_mock_logger_fixture(self, mock_logger):
        """Test the mock_logger fixture provides logging methods."""
        assert hasattr(mock_logger, "debug"), "Logger should have debug method"
        assert hasattr(mock_logger, "info"), "Logger should have info method"
        assert hasattr(mock_logger, "error"), "Logger should have error method"
        
        mock_logger.info("Test message")
        mock_logger.info.assert_called_once_with("Test message")
    
    def test_mock_file_system_fixture(self, mock_file_system):
        """Test the mock file system fixture."""
        test_path = "/test/file.txt"
        test_content = "Hello, World!"
        
        with open(test_path, 'w') as f:
            f.write(test_content)
        
        assert test_path in mock_file_system, "File should be in mock file system"
        assert mock_file_system[test_path] == test_content, "Content should match"
        
        with open(test_path, 'r') as f:
            content = f.read()
        assert content == test_content, "Should be able to read back the content"
    
    def test_sample_data_files_fixture(self, sample_data_files):
        """Test the sample_data_files fixture creates expected files."""
        assert "json" in sample_data_files, "Should have JSON file"
        assert "csv" in sample_data_files, "Should have CSV file"
        assert "text" in sample_data_files, "Should have text file"
        
        json_content = sample_data_files["json"].read_text()
        assert "key" in json_content, "JSON file should contain expected content"
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit marker is available."""
        assert True, "Unit test marker should work"
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker is available."""
        assert True, "Integration test marker should work"
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker is available."""
        assert True, "Slow test marker should work"
    
    def test_captured_logs_fixture(self, captured_logs):
        """Test the captured_logs fixture."""
        logs, capture_log = captured_logs
        
        capture_log("INFO", "Test message", extra="data")
        
        assert len(logs) == 1, "Should have captured one log"
        assert logs[0]["level"] == "INFO", "Log level should match"
        assert logs[0]["message"] == "Test message", "Log message should match"
    
    def test_mock_subprocess_fixture(self, mock_subprocess):
        """Test the mock_subprocess fixture."""
        import subprocess
        
        subprocess.run(["echo", "test"])
        
        assert len(mock_subprocess) == 1, "Should have captured one subprocess call"
        assert mock_subprocess[0]["args"][0] == ["echo", "test"], "Command should match"
    
    def test_clean_environment_fixture(self, clean_environment):
        """Test the clean_environment fixture."""
        assert "HOME" in clean_environment, "Should have HOME in test environment"
        assert clean_environment["HOME"] == "/tmp/test_home", "HOME should be test value"
        assert clean_environment["USER"] == "testuser", "USER should be test value"


class TestCoverageConfiguration:
    """Test that coverage configuration is properly set up."""
    
    def test_coverage_source_configured(self):
        """Test that coverage is configured to track the right sources."""
        import configparser
        from pathlib import Path
        
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        assert pyproject.exists(), "pyproject.toml should exist"
        
        content = pyproject.read_text()
        assert "[tool.coverage.run]" in content, "Coverage run configuration should exist"
        assert '"app"' in content or "'app'" in content, "App should be in coverage sources"
    
    def test_coverage_reporting_configured(self):
        """Test that coverage reporting is properly configured."""
        from pathlib import Path
        
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject.read_text()
        
        assert "[tool.coverage.report]" in content, "Coverage report configuration should exist"
        assert "fail_under = 80" in content, "Coverage threshold should be set to 80%"


class TestPytestConfiguration:
    """Test that pytest is properly configured."""
    
    def test_pytest_ini_configured(self):
        """Test that pytest configuration exists in pyproject.toml."""
        from pathlib import Path
        
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject.read_text()
        
        assert "[tool.pytest.ini_options]" in content, "Pytest configuration should exist"
        assert "testpaths" in content, "Test paths should be configured"
        assert '"tests"' in content or "'tests'" in content, "Tests directory should be in testpaths"
    
    def test_markers_configured(self):
        """Test that custom markers are configured."""
        from pathlib import Path
        
        pyproject = Path(__file__).parent.parent / "pyproject.toml"
        content = pyproject.read_text()
        
        assert "unit:" in content, "Unit test marker should be configured"
        assert "integration:" in content, "Integration test marker should be configured"
        assert "slow:" in content, "Slow test marker should be configured"


def test_project_structure():
    """Test that the project structure is set up correctly."""
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    
    assert (project_root / "tests").exists(), "Tests directory should exist"
    assert (project_root / "tests" / "__init__.py").exists(), "Tests __init__.py should exist"
    assert (project_root / "tests" / "conftest.py").exists(), "conftest.py should exist"
    assert (project_root / "tests" / "unit").exists(), "Unit tests directory should exist"
    assert (project_root / "tests" / "integration").exists(), "Integration tests directory should exist"
    assert (project_root / "pyproject.toml").exists(), "pyproject.toml should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])