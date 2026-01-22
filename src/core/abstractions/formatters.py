"""Абстракции для форматирования отчетов."""

from abc import ABC, abstractmethod
from typing import Any


class IReportFormatter(ABC):
    """Интерфейс для форматирования отчетов."""

    @abstractmethod
    def format(self, statistics: dict[str, Any]) -> str:
        """Форматирует статистику в строку отчета.

        Args:
            statistics: Статистика для форматирования

        Returns:
            str: Отформатированный отчет

        """

    @abstractmethod
    def get_file_extension(self) -> str:
        """Возвращает расширение файла для данного формата.

        Returns:
            str: Расширение файла (например, '.json', '.md')

        """
