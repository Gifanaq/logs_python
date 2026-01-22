"""Фабрика для создания форматтеров отчетов.

Отвечает за выбор правильной реализации IReportFormatter на основе названия формата.
"""

from src.core.abstractions.formatters import IReportFormatter
from src.core.implementations.formatters.adoc_formatter import AdocFormatter
from src.core.implementations.formatters.json_formatter import JsonFormatter
from src.core.implementations.formatters.markdown_formatter import MarkdownFormatter


class FormatterFactory:
    """Фабрика для создания форматтеров отчетов.

    Ответственность:
    - Создание соответствующей реализации IReportFormatter по названию формата
    - Валидация поддерживаемых форматов
    - Инкапсуляция логики выбора форматтера

    Не знает о:
    - Источнике данных
    - Бизнес-логике расчета статистики
    - Ридерах или парсерах
    """

    @staticmethod
    def create_formatter(format_name: str) -> IReportFormatter:
        """Создает форматтер на основе названия формата.

        Args:
            format_name: Название формата ('json', 'markdown', 'adoc')

        Returns:
            IReportFormatter: Соответствующая реализация форматтера

        Raises:
            ValueError: Если формат не поддерживается

        Examples:
            >>> FormatterFactory.create_formatter("json")
            JsonFormatter()

            >>> FormatterFactory.create_formatter("markdown")
            MarkdownFormatter()

            >>> FormatterFactory.create_formatter("adoc")
            AdocFormatter()

        """
        if not format_name:
            msg = "Format name cannot be empty or None"
            raise ValueError(msg)

        format_name = format_name.lower().strip()

        if format_name == "json":
            return JsonFormatter()
        if format_name == "markdown":
            return MarkdownFormatter()
        if format_name == "adoc":
            return AdocFormatter()
        msg = (
            f"Unsupported format: '{format_name}'. "
            f"Supported formats: 'json', 'markdown', 'adoc'"
        )
        raise ValueError(msg)
