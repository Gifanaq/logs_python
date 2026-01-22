import os
import tempfile


class TestEdgeCases:
    """Тесты граничных случаев."""

    def test_empty_file(self, temp_output_dir) -> None:
        """Тест с пустым файлом."""
        from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

        # Создаем пустой файл
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            log_path = f.name

        try:
            output_path = os.path.join(temp_output_dir, "report.json")

            class Args:
                path = log_path
                output = output_path
                format = "json"
                date_from = None
                date_to = None

            analyzer = LogAnalyzerFactory.create()
            result = analyzer.analyze(Args())

            assert result == 0
            assert os.path.exists(output_path)

            # Проверяем что в отчёте 0 запросов
            with open(output_path) as f:
                content = f.read()
                assert '"totalRequestsCount": 0' in content

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)

    def test_file_with_only_invalid_lines(self, temp_output_dir) -> None:
        """Тест с файлом где все строки невалидные."""
        from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

        # Создаем файл с невалидными строками
        log_content = """INVALID LINE 1
NOT A LOG LINE
ANOTHER INVALID LINE"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(log_content)
            log_path = f.name

        try:
            output_path = os.path.join(temp_output_dir, "report.json")

            class Args:
                path = log_path
                output = output_path
                format = "json"
                date_from = None
                date_to = None

            analyzer = LogAnalyzerFactory.create()
            result = analyzer.analyze(Args())

            assert result == 0
            assert os.path.exists(output_path)

            # Проверяем что в отчёте 0 запросов
            with open(output_path) as f:
                content = f.read()
                assert '"totalRequestsCount": 0' in content

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)
