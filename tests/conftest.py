import os
import tempfile

import pytest


@pytest.fixture
def sample_log_file():
    """Фикстура с тестовым лог-файлом."""
    log_content = '''93.180.71.3 - - [17/May/2015:08:05:32 +0000] "GET /downloads/product_1 HTTP/1.1" 304 0 "-" "Debian APT-HTTP/1.3"
80.91.33.133 - - [17/May/2015:08:05:33 +0000] "GET /downloads/product_2 HTTP/1.1" 200 512 "-" "Debian APT-HTTP/1.3"
217.168.17.5 - - [17/May/2015:08:05:34 +0000] "POST /api/users HTTP/2.0" 404 0 "-" "Mozilla/5.0"'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(log_content)
        temp_path = f.name

    yield temp_path

    # Уборка
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def sample_log_file_with_invalid_lines():
    """Фикстура с лог-файлом содержащим некорректные строки."""
    log_content = """93.180.71.3 - - [17/May/2015:08:05:32 +0000] "GET /test HTTP/1.1" 200 100 "-" "Agent"
INVALID LOG LINE
192.168.1.1 - - [17/May/2015:08:05:33 +0000] "POST /api HTTP/1.1" 201 200 "-" "Agent"
ANOTHER INVALID LINE"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(log_content)
        temp_path = f.name

    yield temp_path

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_output_dir():
    """Фикстура с временной директорией для выходных файлов."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def mock_formatter():
    """Фикстура с моком форматтера."""
    from unittest.mock import Mock

    from src.core.abstractions.formatters import IReportFormatter

    formatter = Mock(spec=IReportFormatter)
    formatter.get_file_extension.return_value = ".json"
    formatter.format.return_value = "formatted content"
    return formatter
