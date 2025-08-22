import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any
import pytest
from unittest.mock import Mock, MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file for testing."""
    temp_file = temp_dir / "test_file.txt"
    temp_file.write_text("test content")
    yield temp_file


@pytest.fixture
def mock_config() -> dict:
    """Provide a mock configuration dictionary."""
    return {
        "debug": True,
        "log_level": "INFO",
        "data_dir": "/tmp/test_data",
        "plugins": {
            "enabled": True,
            "directory": "/tmp/plugins"
        },
        "network": {
            "timeout": 30,
            "retry_count": 3
        }
    }


@pytest.fixture
def mock_logger() -> Mock:
    """Provide a mock logger object."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def mock_file_system(monkeypatch) -> dict:
    """Mock file system operations."""
    files = {}
    
    def mock_open(path, mode='r', *args, **kwargs):
        if 'r' in mode:
            if path not in files:
                raise FileNotFoundError(f"No such file: {path}")
            content = files[path]
            mock_file = MagicMock()
            mock_file.read.return_value = content
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            return mock_file
        elif 'w' in mode or 'a' in mode:
            mock_file = MagicMock()
            def write(data):
                if 'w' in mode:
                    files[path] = data
                else:
                    files[path] = files.get(path, '') + data
            mock_file.write = write
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            return mock_file
    
    monkeypatch.setattr('builtins.open', mock_open)
    return files


@pytest.fixture
def mock_network_response():
    """Provide a mock network response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"status": "success", "data": []}
    response.text = '{"status": "success", "data": []}'
    response.content = b'{"status": "success", "data": []}'
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture
def sample_data_files(temp_dir: Path) -> dict:
    """Create sample data files for testing."""
    data_files = {}
    
    json_file = temp_dir / "sample.json"
    json_file.write_text('{"key": "value", "items": [1, 2, 3]}')
    data_files["json"] = json_file
    
    csv_file = temp_dir / "sample.csv"
    csv_file.write_text("header1,header2,header3\nvalue1,value2,value3\n")
    data_files["csv"] = csv_file
    
    text_file = temp_dir / "sample.txt"
    text_file.write_text("Line 1\nLine 2\nLine 3\n")
    data_files["text"] = text_file
    
    return data_files


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime for consistent testing."""
    import datetime
    mock_dt = Mock()
    mock_dt.now.return_value = datetime.datetime(2024, 1, 1, 12, 0, 0)
    mock_dt.utcnow.return_value = datetime.datetime(2024, 1, 1, 12, 0, 0)
    monkeypatch.setattr('datetime.datetime', mock_dt)
    return mock_dt


@pytest.fixture
def clean_environment(monkeypatch):
    """Clean environment variables for testing."""
    test_env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "HOME": "/tmp/test_home",
        "USER": "testuser"
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    for key in list(os.environ.keys()):
        if key not in test_env:
            monkeypatch.delenv(key, raising=False)
    
    return test_env


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    yield


@pytest.fixture
def captured_logs():
    """Capture log messages for testing."""
    logs = []
    
    def capture_log(level, message, *args, **kwargs):
        logs.append({
            "level": level,
            "message": message,
            "args": args,
            "kwargs": kwargs
        })
    
    return logs, capture_log


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess calls."""
    calls = []
    
    def mock_run(*args, **kwargs):
        calls.append({"args": args, "kwargs": kwargs})
        result = Mock()
        result.returncode = 0
        result.stdout = "Mock output"
        result.stderr = ""
        return result
    
    monkeypatch.setattr("subprocess.run", mock_run)
    monkeypatch.setattr("subprocess.call", lambda *args, **kwargs: 0)
    monkeypatch.setattr("subprocess.check_call", lambda *args, **kwargs: None)
    monkeypatch.setattr("subprocess.check_output", lambda *args, **kwargs: b"Mock output")
    
    return calls


@pytest.fixture
def async_mock():
    """Create an async mock for testing async functions."""
    import asyncio
    
    async def async_return(value):
        return value
    
    mock = MagicMock()
    mock.return_value = async_return("async_result")
    return mock


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)