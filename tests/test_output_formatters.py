import json

import pytest


class TestOutputFormatters:
    """Тесты форматтеров вывода (Кейсы 16-18)."""

    # Кейс 16
    def test_json_formatter(self) -> None:
        """Кейс 16: Сохранение статистики в формате JSON."""
        from src.core.implementations.formatters.json_formatter import JsonFormatter

        formatter = JsonFormatter()
        test_statistics = {
            "totalRequestsCount": 100,
            "responseSizeInBytes": {"average": 500, "max": 1000, "p95": 950},
            "resources": [{"resource": "/test", "totalRequestsCount": 50}],
            "responseCodes": [{"code": 200, "totalResponsesCount": 80}],
        }

        result = formatter.format(test_statistics)

        # Проверяем что это валидный JSON
        parsed_json = json.loads(result)
        assert parsed_json["totalRequestsCount"] == 100
        assert parsed_json["responseSizeInBytes"]["average"] == 500

        # Проверяем расширение
        assert formatter.get_file_extension() == ".json"

    # Кейс 17
    def test_markdown_formatter(self) -> None:
        """Кейс 17: Сохранение статистики в формате MARKDOWN."""
        from src.core.implementations.formatters.markdown_formatter import (
            MarkdownFormatter,
        )

        formatter = MarkdownFormatter()
        test_statistics = {
            "files": ["test.log"],
            "totalRequestsCount": 100,
            "responseSizeInBytes": {"average": 500, "max": 1000, "p95": 950},
            "resources": [
                {"resource": "/test1", "totalRequestsCount": 50},
                {"resource": "/test2", "totalRequestsCount": 30},
            ],
            "responseCodes": [
                {"code": 200, "totalResponsesCount": 80},
                {"code": 404, "totalResponsesCount": 10},
            ],
            "requestsPerDate": [
                {
                    "date": "2025-01-01",
                    "weekday": "Wednesday",
                    "totalRequestsCount": 100,
                    "totalRequestsPercentage": 100.0,
                }
            ],
            "uniqueProtocols": ["HTTP/1.1", "HTTP/2.0"],
        }

        result = formatter.format(test_statistics)

        # Проверяем основные секции
        assert "#### Общая информация" in result
        assert "#### Запрашиваемые ресурсы" in result
        assert "#### Коды ответа" in result
        assert "100" in result  # Должны быть числа
        assert formatter.get_file_extension() == ".md"

    # Кейс 18
    def test_adoc_formatter(self) -> None:
        """Кейс 18: Сохранение статистики в формате ADOC."""
        from src.core.implementations.formatters.adoc_formatter import AdocFormatter

        formatter = AdocFormatter()
        test_statistics = {
            "files": ["test.log"],
            "totalRequestsCount": 100,
            "responseSizeInBytes": {"average": 500, "max": 1000, "p95": 950},
            "resources": [{"resource": "/test", "totalRequestsCount": 50}],
            "responseCodes": [{"code": 200, "totalResponsesCount": 80}],
            "requestsPerDate": [
                {
                    "date": "2025-01-01",
                    "weekday": "Wednesday",
                    "totalRequestsCount": 100,
                    "totalRequestsPercentage": 100.0,
                }
            ],
            "uniqueProtocols": ["HTTP/1.1"],
        }

        result = formatter.format(test_statistics)

        # Проверяем основные секции AsciiDoc
        assert "==== Общая информация" in result
        assert "|===" in result  # Таблицы
        assert "100" in result
        assert formatter.get_file_extension() == ".adoc"

    # Дополнительный тест - все форматы с одинаковыми данными
    @pytest.mark.parametrize(
        ("formatter_class", "extension"),
        [
            ("JsonFormatter", ".json"),
            ("MarkdownFormatter", ".md"),
            ("AdocFormatter", ".adoc"),
        ],
    )
    def test_all_formatters_with_same_data(
        self, formatter_class: str, extension: str
    ) -> None:
        """Тест всех форматтеров с одинаковыми данными."""
        from src.core.implementations.formatters.adoc_formatter import AdocFormatter
        from src.core.implementations.formatters.json_formatter import JsonFormatter
        from src.core.implementations.formatters.markdown_formatter import (
            MarkdownFormatter,
        )

        formatters = {
            "JsonFormatter": JsonFormatter(),
            "MarkdownFormatter": MarkdownFormatter(),
            "AdocFormatter": AdocFormatter(),
        }

        formatter = formatters[formatter_class]
        test_data = {
            "totalRequestsCount": 42,
            "responseSizeInBytes": {"average": 100, "max": 500, "p95": 450},
            "resources": [],
            "responseCodes": [],
        }

        result = formatter.format(test_data)
        assert formatter.get_file_extension() == extension
        assert "42" in result or "totalRequestsCount" in result
