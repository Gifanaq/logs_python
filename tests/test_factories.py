import pytest


class TestFactories:
    """Тесты фабрик."""

    @pytest.mark.parametrize(
        ("path", "expected_reader_type"),
        [
            ("/var/log/nginx/access.log", "LocalFileReader"),
            ("logs/*.log", "LocalFileReader"),
            ("https://example.com/logs/access.log", "UrlReader"),
            ("http://example.com/logs/access.log", "UrlReader"),
        ],
    )
    def test_reader_factory(self, path, expected_reader_type) -> None:
        """Тест фабрики ридеров."""
        from src.infrastructure.factories.reader_factory import ReaderFactory

        reader = ReaderFactory.create_reader(path)

        assert reader.__class__.__name__ == expected_reader_type

    @pytest.mark.parametrize(
        ("format_name", "expected_formatter_type"),
        [
            ("json", "JsonFormatter"),
            ("markdown", "MarkdownFormatter"),
            ("adoc", "AdocFormatter"),
        ],
    )
    def test_formatter_factory(self, format_name, expected_formatter_type) -> None:
        """Тест фабрики форматтеров."""
        from src.infrastructure.factories.formatter_factory import FormatterFactory

        formatter = FormatterFactory.create_formatter(format_name)

        assert formatter.__class__.__name__ == expected_formatter_type

    def test_log_analyzer_factory(self) -> None:
        """Тест фабрики анализатора логов."""
        from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

        analyzer = LogAnalyzerFactory.create()

        assert hasattr(analyzer, "analyze")
        assert hasattr(analyzer, "reader_factory")
        assert hasattr(analyzer, "parser")
        assert hasattr(analyzer, "calculator")
        assert hasattr(analyzer, "formatter_factory")
