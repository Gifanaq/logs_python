"""Реализация парсера для логов NGINX."""

import logging
import re
from collections.abc import Iterator
from datetime import datetime

from src.core.abstractions.parsers import ILogParser
from src.models.log_entry import LogEntry

logger = logging.getLogger(__name__)


class NginxLogParser(ILogParser):
    """Реализация ILogParser для логов NGINX.

    Компромисс между SOLID и требованиями ТЗ: минимальное необходимое логирование.
    """

    LOG_PATTERN = re.compile(
        r"^(?P<remote_addr>\S+) - (?P<remote_user>\S+) \[(?P<time_local>[^\]]+)\] "
        r'"(?P<request>[^"]*)" (?P<status>\d+) (?P<body_bytes_sent>\d+) '
        r'"(?P<http_referer>[^"]*)" "(?P<http_user_agent>[^"]*)"$'
    )

    TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"

    def parse_lines(self, lines: Iterator[str]) -> list[LogEntry]:
        """Парсит итератор строк в список LogEntry.

        Соответствует ТЗ: логирует WARN для некорректных строк.
        """
        entries = []

        for line in lines:
            if not line.strip():
                continue

            try:
                entry = self.parse_line(line)
                entries.append(entry)
            except ValueError as e:
                logger.warning(
                    f"Строка не соответствует формату NGINX и будет пропущена: {e}"
                )
            except Exception:
                # Критическая ошибка - fail-fast!
                logger.exception("Критическая ошибка парсинга")
                raise

        return entries

    def parse_line(self, line: str) -> LogEntry:
        """Чистый парсинг одной строки.

        Без логирования - только преобразование данных.
        """
        if not line or line.isspace():
            msg = "Пустая строка"
            raise ValueError(msg)

        match = self.LOG_PATTERN.match(line)
        if not match:
            msg = "Не соответствует формату NGINX"
            raise ValueError(msg)

        groups = match.groupdict()

        # Все преобразования могут бросить ValueError - это нормально
        return LogEntry(
            remote_addr=groups["remote_addr"],
            remote_user=self._parse_remote_user(groups["remote_user"]),
            time_local=self._parse_time(groups["time_local"]),
            request=groups["request"],
            status=int(groups["status"]),
            body_bytes_sent=int(groups["body_bytes_sent"]),
            http_referer=groups["http_referer"],
            http_user_agent=groups["http_user_agent"],
        )

    def _parse_remote_user(self, raw_user: str) -> None | str:
        """Преобразует remote_user. '-' → None."""
        return None if raw_user == "-" else raw_user

    def _parse_time(self, time_str: str) -> datetime:
        """Парсит время из формата NGINX."""
        return datetime.strptime(time_str, self.TIME_FORMAT)
