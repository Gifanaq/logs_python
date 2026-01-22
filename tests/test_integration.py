import os
import tempfile

import pytest


class TestIntegration:
    """Интеграционные тесты полного workflow."""

    def test_complete_workflow_with_real_file(self, temp_output_dir: str) -> None:
        """Полный workflow с реальным файлом: чтение → парсинг → расчет → вывод."""
        from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

        # Создаем реальный тестовый лог-файл
        log_content = '''93.180.71.3 - - [17/May/2015:08:05:32 +0000] "GET /downloads/product_1 HTTP/1.1" 304 0 "-" "Debian APT-HTTP/1.3"
80.91.33.133 - - [17/May/2015:08:05:33 +0000] "GET /downloads/product_2 HTTP/1.1" 200 512 "-" "Debian APT-HTTP/1.3"
217.168.17.5 - - [17/May/2015:08:05:34 +0000] "POST /api/users HTTP/2.0" 404 0 "-" "Mozilla/5.0"'''

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

            # Проверяем что завершилось успешно
            assert result == 0

            # Проверяем что файл создался
            assert os.path.exists(output_path)

            # Проверяем базовое содержимое
            with open(output_path) as f:
                content = f.read()
                assert '"totalRequestsCount": 3' in content
                assert '"resources"' in content

        finally:
            # Уборка
            if os.path.exists(log_path):
                os.unlink(log_path)

    def test_all_formats_with_real_data(self, temp_output_dir: str) -> None:
        """Тест всех форматов вывода с одинаковыми данными."""
        from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

        # Создаем реальный тестовый лог-файл
        log_content = '''93.180.71.3 - - [17/May/2015:08:05:32 +0000] "GET /test HTTP/1.1" 200 100 "-" "Agent"'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write(log_content)
            log_path = f.name

        try:
            for format_name, extension in [
                ("json", ".json"),
                ("markdown", ".md"),
                ("adoc", ".adoc"),
            ]:
                output_path = os.path.join(temp_output_dir, f"report{extension}")

                class Args:
                    path = log_path
                    output = output_path
                    format = format_name
                    date_from = None
                    date_to = None

                analyzer = LogAnalyzerFactory.create()
                result = analyzer.analyze(Args())

                assert result == 0
                assert os.path.exists(output_path)

                # Проверяем что файл не пустой
                with open(output_path, encoding="utf-8") as f:
                    content = f.read()
                    assert len(content) > 0
                    if format_name == "json":
                        assert '"totalRequestsCount": 1' in content
                    else:
                        assert "1" in content  # Хотя бы число запросов должно быть

        finally:
            if os.path.exists(log_path):
                os.unlink(log_path)

    @pytest.mark.skip(reason="Требует интернет соединения")
    def test_real_remote_file_integration(self) -> None:
        """Интеграционный тест с реальным удалённым файлом (требует интернет)."""
        import requests

        from src.core.implementations.parsers.log_parser import NginxLogParser
        from src.core.implementations.readers.url_reader import UrlReader

        reader = UrlReader()
        parser = NginxLogParser()

        try:
            # Реальный URL с логами NGINX
            url = "https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_logs/nginx_logs"
            lines = list(reader.read_files(url))
            entries = parser.parse_lines(iter(lines))

            # Должен быть хотя бы один валидный лог
            assert len(entries) > 0
            assert entries[0].status in [200, 304, 404]  # Должен быть валидный статус

        except (OSError, requests.RequestException, ValueError) as e:
            pytest.skip(f"Не удалось загрузить удалённый файл: {e}")
