from datetime import datetime

from src.models.log_entry import LogEntry


class DateFilterService:
    """Сервис для фильтрации дат."""

    @staticmethod
    def filter_entries(
        entries: list[LogEntry], date_from_str: str, date_to_str: str
    ) -> list[LogEntry]:
        """Фильтрует по датам."""
        if not date_from_str and not date_to_str:
            return entries

        date_from = datetime.fromisoformat(date_from_str) if date_from_str else None
        date_to = datetime.fromisoformat(date_to_str) if date_to_str else None

        # Расширяем date_to до конца дня ВСЕГДА когда он указан
        if date_to:
            date_to = date_to.replace(hour=23, minute=59, second=59, microsecond=999999)

        filtered_entries = []
        for entry in entries:
            entry_dt = entry.time_local.replace(tzinfo=None)

            if date_from and entry_dt < date_from:
                continue
            if date_to and entry_dt > date_to:
                continue

            filtered_entries.append(entry)

        return filtered_entries
