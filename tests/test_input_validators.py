import os
import sys

import pytest


class TestInputValidation:
    """Тесты валидации входных данных - Кейсы 1-10."""

    # ==================== КЕЙС 1 ====================
    def test_nonexistent_local_file(self) -> None:
        """КЕЙС 1: На вход передан несуществующий локальный файл."""
        from src.core.implementations.readers.file_reader import LocalFileReader

        reader = LocalFileReader()
        with pytest.raises(FileNotFoundError):
            list(reader.read_files("nonexistent_file.log"))

    # ==================== КЕЙС 2 ====================
    def test_nonexistent_remote_file(self, monkeypatch) -> None:
        """КЕЙС 2: На вход передан несуществующий удаленный файл."""
        from collections.abc import Iterator
        from unittest.mock import Mock

        from requests.exceptions import HTTPError

        from src.core.implementations.readers.url_reader import UrlReader

        def mock_get(url, **kwargs) -> Mock:
            class MockResponse:
                status_code = 404
                headers = {}

                def raise_for_status(self) -> None:
                    error = HTTPError("404 Client Error: Not Found")
                    error.response = self
                    raise error

                def iter_lines(self) -> Iterator[str]:
                    return iter([])

            return MockResponse()

        monkeypatch.setattr(
            "src.core.implementations.readers.url_reader.requests.get", mock_get
        )

        reader = UrlReader()
        with pytest.raises(FileNotFoundError, match="URL не найден"):
            list(reader.read_files("https://example.com/nonexistent.log"))

    # ==================== КЕЙС 3 ====================
    @pytest.mark.parametrize(
        "invalid_extension",
        ["file.csv", "file.pdf", "file.docx", "file.xml", "file.zip"],
    )
    def test_unsupported_file_formats(self, invalid_extension) -> None:
        """КЕЙС 3: На вход передан файл в неподдерживаемом формате."""
        from src.domain.validators.file_format_validator import FileFormatValidator

        validator = FileFormatValidator()
        with pytest.raises(ValueError, match="Неподдерживаемый формат файла"):
            validator.validate_extension(invalid_extension)

    # ==================== КЕЙС 4 ====================
    @pytest.mark.parametrize(
        ("date_from", "date_to"),
        [
            ("2025.01.01", "2025-01-02"),  # Не ISO формат
            ("today", "2025-01-02"),  # Строка today
            ("2025-01-01", "tomorrow"),  # Строка tomorrow
            ("01-01-2025", "02-01-2025"),  # ДД-ММ-ГГГГ
            ("2025/01/01", "2025/01/02"),  # Слеши вместо дефисов
        ],
    )
    def test_invalid_date_formats(self, date_from, date_to) -> None:
        """КЕЙС 4: На вход переданы невалидные параметры --from / --to."""
        from src.domain.validators.args_validator import ArgsValidator

        class Args:
            pass

        args = Args()
        args.date_from = date_from
        args.date_to = date_to

        with pytest.raises(ValueError):
            ArgsValidator.validate_args(args)

    # ==================== КЕЙС 5 ====================
    @pytest.mark.parametrize("invalid_format", ["txt", "xml", "csv", "html", "yaml"])
    def test_unsupported_output_formats(self, invalid_format) -> None:
        """КЕЙС 5: Результаты запрошены в неподдерживаемом формате."""
        from src.infrastructure.factories.formatter_factory import FormatterFactory

        with pytest.raises(ValueError, match="Unsupported format"):
            FormatterFactory.create_formatter(invalid_format)

    # ==================== КЕЙС 6 ====================
    @pytest.mark.parametrize(
        ("output_file", "formatter_extension"),
        [
            ("report.txt", ".json"),
            ("report.md", ".json"),
            ("data.xml", ".json"),
            ("report.json", ".md"),
            ("report.adoc", ".json"),
        ],
    )
    def test_output_incorrect_extensions(
        self, temp_output_dir, output_file, formatter_extension
    ) -> None:
        """КЕЙС 6: По пути в --output указан файл с некорректным расширением."""
        from unittest.mock import Mock

        from src.core.abstractions.formatters import IReportFormatter
        from src.domain.validators.output_validator import OutputValidator

        mock_formatter = Mock(spec=IReportFormatter)
        mock_formatter.get_file_extension.return_value = formatter_extension

        output_path = os.path.join(temp_output_dir, output_file)
        with pytest.raises(ValueError, match=f"Ожидается: '{formatter_extension}'"):
            OutputValidator.validate_output_path(output_path, mock_formatter)

    # ==================== КЕЙС 7 ====================
    def test_output_file_exists(self, temp_output_dir, mock_formatter) -> None:
        """КЕЙС 7: По пути в --output уже существует файл."""
        from src.domain.validators.output_validator import OutputValidator

        output_path = os.path.join(temp_output_dir, "report.json")
        with open(output_path, "w") as f:
            f.write("content")

        with pytest.raises(ValueError, match="Файл уже существует"):
            OutputValidator.validate_output_path(output_path, mock_formatter)

    # ==================== КЕЙС 8 ====================
    @pytest.mark.parametrize(
        "missing_args",
        [
            [],  # Все аргументы отсутствуют
            ["--path", "test.log"],  # Нет --output и --format
            ["--output", "report.json"],  # Нет --path и --format
            ["--format", "json"],  # Нет --path и --output
            ["--path", "test.log", "--output", "report.json"],  # Нет --format
        ],
    )
    def test_missing_required_arguments(self, missing_args, monkeypatch) -> None:
        """КЕЙС 8: Не передан обязательный параметр."""
        from src.main import main

        # Мокаем sys.argv с отсутствующими обязательными аргументами
        def mock_argv() -> list[str]:
            return ["main.py", *missing_args]

        monkeypatch.setattr(sys, "argv", mock_argv())

        # Должен вернуть код ошибки 2 (некорректное использование)
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2

    # ==================== КЕЙС 9 ====================
    @pytest.mark.parametrize(
        "unsupported_args",
        [
            ["--input", "data.log"],  # Неподдерживаемый --input
            ["--filter", "some_filter"],  # Неподдерживаемый --filter
            ["--verbose", "--debug"],  # Неподдерживаемые флаги
            [
                "--path",
                "test.log",
                "--output",
                "report.json",
                "--format",
                "json",
                "--unknown",
                "value",
            ],  # Смешанные
        ],
    )
    def test_unsupported_arguments(self, unsupported_args, monkeypatch) -> None:
        """КЕЙС 9: На вход передан неподдерживаемый параметр."""
        from src.main import main

        # Базовые обязательные аргументы + неподдерживаемые
        base_args = [
            "--path",
            "test.log",
            "--output",
            "report.json",
            "--format",
            "json",
        ]

        def mock_argv() -> list[str]:
            return ["main.py", *base_args, *unsupported_args]

        monkeypatch.setattr(sys, "argv", mock_argv())

        # Должен вернуть код ошибки 2 (некорректное использование)
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 2

    # ==================== КЕЙС 10 ====================
    @pytest.mark.parametrize(
        ("date_from", "date_to"),
        [
            ("2025-01-02", "2025-01-01"),  # День позже
            ("2025-02-01", "2025-01-01"),  # Месяц позже
            ("2026-01-01", "2025-01-01"),  # Год позже
            ("2025-01-01T10:00:00", "2025-01-01T09:00:00"),  # Время позже
        ],
    )
    def test_from_greater_than_to_cases(self, date_from: str, date_to: str) -> None:
        """КЕЙС 10: Значение --from больше, чем значение --to."""
        from src.domain.validators.args_validator import ArgsValidator

        class Args:
            pass

        args = Args()
        args.date_from = date_from
        args.date_to = date_to

        with pytest.raises(
            ValueError, match="Дата 'from' должна быть меньше даты 'to'"
        ):
            ArgsValidator.validate_args(args)
