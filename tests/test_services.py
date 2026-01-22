from datetime import datetime


class TestServices:
    """Дополнительные тесты сервисов."""

    def test_request_parser_service(self) -> None:
        """Тест сервиса парсинга HTTP запросов."""
        from src.domain.services.request_parser_service import RequestParserService

        service = RequestParserService()

        # Тест извлечения ресурса
        assert service.extract_resource("GET /api/users HTTP/1.1") == "/api/users"
        assert service.extract_resource("POST /data HTTP/2.0") == "/data"
        assert service.extract_resource("") == "/"

        # Тест извлечения протокола
        assert service.extract_protocol("GET /api/users HTTP/1.1") == "HTTP/1.1"
        assert service.extract_protocol("POST /data HTTP/2") == "HTTP/2"
        assert service.extract_protocol("INVALID") == "UNKNOWN"

    def test_size_statistics_calculator(self) -> None:
        """Тест калькулятора статистики размеров."""
        from src.domain.calculators.size_statistics_calculator import (
            SizeStatisticsCalculator,
        )

        calculator = SizeStatisticsCalculator()

        # Тест с данными
        sizes = [100, 200, 300, 400, 500]
        result = calculator.calculate(sizes)

        assert result["average"] == 300
        assert result["max"] == 500
        assert result["p95"] == 480  # Примерное значение

        # Тест с пустыми данными
        empty_result = calculator.calculate([])
        assert empty_result["average"] == 0
        assert empty_result["max"] == 0
        assert empty_result["p95"] == 0

    def test_data_accumulator(self) -> None:
        """Тест аккумулятора данных."""
        from src.domain.accumulators.data_accumulator import DataAccumulator
        from src.domain.services.request_parser_service import RequestParserService
        from src.models.log_entry import LogEntry

        accumulator = DataAccumulator(RequestParserService())

        entries = [
            LogEntry(
                "1.1.1.1",
                None,
                datetime(2025, 1, 1),
                "GET /test1 HTTP/1.1",
                200,
                100,
                "-",
                "Agent",
            ),
            LogEntry(
                "2.2.2.2",
                None,
                datetime(2025, 1, 1),
                "GET /test2 HTTP/1.1",
                200,
                200,
                "-",
                "Agent",
            ),
            LogEntry(
                "3.3.3.3",
                None,
                datetime(2025, 1, 2),
                "POST /test1 HTTP/2.0",
                404,
                0,
                "-",
                "Agent",
            ),
        ]

        accumulated_data = accumulator.accumulate(entries)

        assert accumulated_data["response_sizes"] == [100, 200, 0]
        assert accumulated_data["resource_frequency"]["/test1"] == 2
        assert accumulated_data["resource_frequency"]["/test2"] == 1
        assert accumulated_data["status_frequency"][200] == 2
        assert accumulated_data["status_frequency"][404] == 1
        assert accumulated_data["date_distribution"]["2025-01-01"] == 2
        assert accumulated_data["date_distribution"]["2025-01-02"] == 1
        assert "HTTP/1.1" in accumulated_data["unique_protocols"]
        assert "HTTP/2.0" in accumulated_data["unique_protocols"]
