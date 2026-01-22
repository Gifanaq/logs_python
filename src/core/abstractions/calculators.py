"""Абстракции для расчета статистики."""

from abc import ABC, abstractmethod
from typing import Any

from src.models.log_entry import LogEntry


class IStatisticsCalculator(ABC):
    """Интерфейс для расчета статистики логов."""

    @abstractmethod
    def calculate(self, entries: list[LogEntry]) -> dict[str, Any]:
        """Рассчитывает статистику по записям логов.

        Returns:
            Dict[str, Any]: Статистика в соответствии с JSON-схемой ТЗ

        """
