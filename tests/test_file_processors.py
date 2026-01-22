from datetime import datetime


class TestFileProcessing:
    """Тесты обработки файлов (Кейсы 11-15)."""

    # ==================== КЕЙС 11 ====================
    def test_valid_local_file_reading(self, sample_log_file) -> None:
        """КЕЙС 11: На вход передан валидный локальный log-файл."""
        from src.core.implementations.parsers.log_parser import NginxLogParser
        from src.core.implementations.readers.file_reader import LocalFileReader

        reader = LocalFileReader()
        parser = NginxLogParser()

        lines = list(reader.read_files(sample_log_file))
        entries = parser.parse_lines(iter(lines))

        assert len(entries) == 3
        assert entries[0].status == 304
        assert entries[1].status == 200
        assert entries[2].status == 404
        assert entries[0].request == "GET /downloads/product_1 HTTP/1.1"
        assert entries[1].request == "GET /downloads/product_2 HTTP/1.1"
        assert entries[2].request == "POST /api/users HTTP/2.0"

    # ==================== КЕЙС 12 ====================
    def test_valid_remote_file_reading(self, monkeypatch) -> None:
        """КЕЙС 12: На вход передан валидный удаленный log-файл."""
        from collections.abc import Iterator
        from unittest.mock import Mock

        from requests.exceptions import HTTPError

        from src.core.implementations.parsers.log_parser import NginxLogParser
        from src.core.implementations.readers.url_reader import UrlReader

        def mock_get(url, **kwargs) -> Mock:
            class MockResponse:
                status_code = 200
                headers = {"Content-Type": "text/plain"}

                def raise_for_status(self) -> None:
                    if self.status_code >= 400:
                        msg = f"HTTP Error {self.status_code}"
                        raise HTTPError(msg)

                def iter_lines(self, **kwargs) -> Iterator[str]:
                    return iter(
                        [
                            '93.180.71.3 - - [17/May/2015:08:05:32 +0000] "GET /test HTTP/1.1" 200 100 "-" "Agent"',
                            '192.168.1.1 - - [17/May/2015:08:05:33 +0000] "POST /api HTTP/1.1" 201 200 "-" "Agent"',
                        ]
                    )

            return MockResponse()

        monkeypatch.setattr(
            "src.core.implementations.readers.url_reader.requests.get", mock_get
        )

        reader = UrlReader()
        parser = NginxLogParser()

        lines = list(reader.read_files("https://example.com/access.log"))
        entries = parser.parse_lines(iter(lines))

        assert len(entries) == 2
        assert entries[0].request == "GET /test HTTP/1.1"
        assert entries[1].request == "POST /api HTTP/1.1"
        assert entries[0].status == 200
        assert entries[1].status == 201
        assert entries[0].body_bytes_sent == 100
        assert entries[1].body_bytes_sent == 200

    # ==================== КЕЙС 13 ====================
    def test_date_filtering(self) -> None:
        """КЕЙС 13: Фильтрация по --from и --to."""
        from src.domain.services.date_filter_service import DateFilterService
        from src.models.log_entry import LogEntry

        entries = [
            LogEntry(
                "1.1.1.1",
                None,
                datetime(2025, 1, 1),
                "GET /test HTTP/1.1",
                200,
                100,
                "-",
                "Agent",
            ),
            LogEntry(
                "2.2.2.2",
                None,
                datetime(2025, 1, 15),
                "POST /api HTTP/1.1",
                201,
                200,
                "-",
                "Agent",
            ),
            LogEntry(
                "3.3.3.3",
                None,
                datetime(2025, 1, 30),
                "PUT /data HTTP/1.1",
                200,
                150,
                "-",
                "Agent",
            ),
        ]

        # Фильтрация с 10 по 20 января
        filtered = DateFilterService.filter_entries(entries, "2025-01-10", "2025-01-20")

        assert len(filtered) == 1
        assert filtered[0].remote_addr == "2.2.2.2"
        assert filtered[0].time_local.date() == datetime(2025, 1, 15).date()

    # ==================== КЕЙС 14 ====================
    def test_file_with_invalid_lines(self, sample_log_file_with_invalid_lines) -> None:
        """КЕЙС 14: Файл с некорректными строками."""
        from src.core.implementations.parsers.log_parser import NginxLogParser
        from src.core.implementations.readers.file_reader import LocalFileReader

        reader = LocalFileReader()
        parser = NginxLogParser()

        lines = list(reader.read_files(sample_log_file_with_invalid_lines))
        entries = parser.parse_lines(iter(lines))

        # Должны быть обработаны только 2 валидные строки из 4
        assert len(entries) == 2
        assert entries[0].status == 200
        assert entries[1].status == 201
        # Некорректные строки должны быть пропущены

    # ==================== КЕЙС 15 ====================
    def test_statistics_calculation(self, sample_log_file) -> None:
        """КЕЙС 15: Расчет статистики."""
        from src.core.implementations.calculators.nginx_statistics_calculator import (
            NginxStatisticsCalculator,
        )
        from src.core.implementations.parsers.log_parser import NginxLogParser
        from src.core.implementations.readers.file_reader import LocalFileReader

        reader = LocalFileReader()
        parser = NginxLogParser()
        calculator = NginxStatisticsCalculator()

        lines = list(reader.read_files(sample_log_file))
        entries = parser.parse_lines(iter(lines))
        statistics = calculator.calculate(entries)

        # Проверяем базовую статистику
        assert statistics["totalRequestsCount"] == 3

        # Проверяем статистику размеров
        assert statistics["responseSizeInBytes"]["average"] == 170.67
        assert statistics["responseSizeInBytes"]["max"] == 512
        assert statistics["responseSizeInBytes"]["p95"] == 460.8

        # Проверяем топ ресурсов
        assert len(statistics["resources"]) == 3
        resources_dict = {
            r["resource"]: r["totalRequestsCount"] for r in statistics["resources"]
        }
        assert resources_dict["/downloads/product_1"] == 1
        assert resources_dict["/downloads/product_2"] == 1
        assert resources_dict["/api/users"] == 1

        # Проверяем коды ответа
        assert len(statistics["responseCodes"]) == 3
        codes_dict = {
            c["code"]: c["totalResponsesCount"] for c in statistics["responseCodes"]
        }
        assert codes_dict[200] == 1
        assert codes_dict[304] == 1
        assert codes_dict[404] == 1

        # Проверяем распределение по датам (доп. баллы)
        if "requestsPerDate" in statistics:
            assert len(statistics["requestsPerDate"]) == 1
            assert statistics["requestsPerDate"][0]["date"] == "2015-05-17"
            assert statistics["requestsPerDate"][0]["totalRequestsCount"] == 3
            assert statistics["requestsPerDate"][0]["totalRequestsPercentage"] == 100.0

        # Проверяем уникальные протоколы (доп. баллы)
        if "uniqueProtocols" in statistics:
            assert "HTTP/1.1" in statistics["uniqueProtocols"]
            assert "HTTP/2.0" in statistics["uniqueProtocols"]
