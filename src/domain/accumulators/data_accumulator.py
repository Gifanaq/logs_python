"""Аккумулятор данных для статистики.

Отвечает ТОЛЬКО за однопроходный сбор и агрегацию данных.
"""

from collections import Counter, defaultdict
from typing import Any

from src.domain.services.request_parser_service import RequestParserService
from src.models.log_entry import LogEntry


class DataAccumulator:
    """Однопроходный аккумулятор данных для статистики логов NGINX.

    Ответственность:
    - Сбор всех необходимых метрик за один проход по данным
    - Агрегация счетчиков и множеств
    - Эффективное использование памяти

    Не знает о:
    - Как данные будут использоваться
    - JSON-структуре результата
    - Логировании процесса
    """

    def __init__(self, request_parser: RequestParserService) -> None:
        self.request_parser = request_parser

    def accumulate(self, entries: list[LogEntry]) -> dict[str, Any]:
        """Собирает все необходимые данные за один проход.

        Args:
            entries: Список записей логов для обработки

        Returns:
            Dict с агрегированными данными для последующей обработки

        Performance:
            Time: O(n) - один проход по данным
            Space: O(1) - константная дополнительная память

        """
        sizes = []
        resource_counter = Counter()
        status_counter = Counter()
        date_counter = defaultdict(int)
        protocol_set = set()

        for entry in entries:
            # 1. Размеры ответов (нужны все значения для перцентиля)
            sizes.append(entry.body_bytes_sent)

            # 2. Частота ресурсов
            resource = self.request_parser.extract_resource(entry.request)
            resource_counter[resource] += 1

            # 3. Статистика HTTP-статусов
            status_counter[entry.status] += 1

            # 4. Распределение по датам
            date_str = entry.time_local.date().isoformat()
            date_counter[date_str] += 1

            # 5. Уникальные протоколы
            protocol = self.request_parser.extract_protocol(entry.request)
            protocol_set.add(protocol)

        return {
            "response_sizes": sizes,
            "resource_frequency": resource_counter,
            "status_frequency": status_counter,
            "date_distribution": date_counter,
            "unique_protocols": protocol_set,
        }
