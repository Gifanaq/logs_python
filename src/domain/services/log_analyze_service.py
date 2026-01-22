from argparse import Namespace
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from src.core.implementations.calculators.nginx_statistics_calculator import (
    NginxStatisticsCalculator,
)
from src.core.implementations.parsers.log_parser import NginxLogParser
from src.models.log_entry import LogEntry

if TYPE_CHECKING:
    from src.infrastructure.factories.formatter_factory import FormatterFactory
    from src.infrastructure.factories.reader_factory import ReaderFactory


class LogAnalyzerService:
    """Координатор workflow анализа логов.

    ЕДИНАЯ ОТВЕТСТВЕННОСТЬ:
    - Координация последовательности шагов анализа
    - Передача данных между специализированными компонентами

    НЕ ЗНАЕТ О:
    - Логировании процесса
    - Валидации данных
    - Обработке ошибок
    - Конкретной реализации компонентов
    """

    def __init__(
        self,
        reader_factory: "ReaderFactory",
        parser: NginxLogParser,
        calculator: NginxStatisticsCalculator,
        formatter_factory: "FormatterFactory",
    ) -> None:
        self.reader_factory = reader_factory
        self.parser = parser
        self.calculator = calculator
        self.formatter_factory = formatter_factory

    def analyze(self, args: Namespace) -> int:
        """Координирует выполнение шагов анализа логов."""
        # 1. Координация чтения файлов
        lines = self._coordinate_reading(args.path)

        # 2. Координация парсинга логов
        entries = self._coordinate_parsing(lines)

        # 3. Координация фильтрации по датам
        filtered_entries = self._coordinate_date_filtering(
            entries, args.date_from, args.date_to
        )

        # 4. Координация расчета статистики
        statistics = self._coordinate_calculation(filtered_entries, args.path)

        # 5. Координация форматирования отчета
        report = self._coordinate_formatting(statistics, args.format)

        # 6. Координация сохранения отчета
        self._coordinate_saving(report, args.output, args.format)

        return 0

    def _coordinate_reading(self, path: str) -> Iterator[str]:
        """Координация чтения файлов."""
        reader = self.reader_factory.create_reader(path)
        return reader.read_files(path)

    def _coordinate_parsing(self, lines: Iterator[str]) -> list[LogEntry]:
        """Координация парсинга логов."""
        return self.parser.parse_lines(lines)

    def _coordinate_date_filtering(
        self, entries: list[LogEntry], date_from: str | None, date_to: str | None
    ) -> list[LogEntry]:
        """Координация фильтрации по датам."""
        from src.domain.services.date_filter_service import DateFilterService

        return DateFilterService.filter_entries(entries, date_from, date_to)

    def _coordinate_calculation(
        self, entries: list[LogEntry], path: str
    ) -> dict[str, Any]:
        """Координация расчета статистики."""
        statistics = self.calculator.calculate(entries)

        import glob
        from pathlib import Path

        actual_files = glob.glob(path)

        # Берем только имена файлов без полного пути
        file_names = [Path(file_path).name for file_path in actual_files]

        statistics["files"] = file_names
        return statistics

    def _coordinate_formatting(
        self, statistics: dict[str, Any], format_name: str
    ) -> str:
        """Координация форматирования отчета."""
        formatter = self.formatter_factory.create_formatter(format_name)
        return formatter.format(statistics)

    def _coordinate_saving(
        self, report: str, output_path: str, format_name: str
    ) -> None:
        """Координация сохранения отчета."""
        from src.domain.services.report_saver import ReportSaver
        from src.domain.validators.output_validator import OutputValidator

        formatter = self.formatter_factory.create_formatter(format_name)

        # Валидация выходного файла
        OutputValidator.validate_output_path(output_path, formatter)

        # Сохранение отчета
        ReportSaver.save_report(report, output_path)
