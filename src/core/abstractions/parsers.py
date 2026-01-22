"""Абстракции для парсинга данных."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from src.models.log_entry import LogEntry


class ILogParser(ABC):
    """Базовый интерфейс для всех парсеров логов."""

    @abstractmethod
    def parse_lines(self, lines: Iterator[str]) -> list[LogEntry]:
        """Парсит итератор строк в список LogEntry."""

    @abstractmethod
    def parse_line(self, line: str) -> LogEntry:
        """Парсит одну строку лога."""
