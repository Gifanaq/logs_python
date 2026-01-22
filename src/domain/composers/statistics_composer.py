"""Компоновщик финальной статистики.

Отвечает ТОЛЬКО за формирование итоговой JSON-структуры.

Это внутренний утилитный класс, который знает о структуре выходных данных.
Инкапсулирует знание о JSON-схеме из ТЗ.
"""

from collections import Counter
from datetime import datetime
from typing import Any

from src.domain.calculators.size_statistics_calculator import SizeStatisticsCalculator


class StatisticsComposer:
    """Компоновщик финальной статистики для анализа логов NGINX.

    Ответственность:
    - Преобразование агрегированных данных в JSON-структуру по ТЗ
    - Форматирование дат и процентных соотношений
    - Сортировка и ограничение топ-ресурсов
    - Гарантия соответствия JSON-схеме

    Не знает о том, как данные были собраны - только как их представить.
    """

    def __init__(self, size_calculator: SizeStatisticsCalculator) -> None:
        self.size_calculator = size_calculator

    def compose(
        self, data_accumulator: dict[str, Any], total_requests: int
    ) -> dict[str, Any]:
        """Компонует финальную статистику из агрегированных данных.

        Args:
            data_accumulator: Словарь с агрегированными данными от DataAccumulator
            total_requests: Общее количество запросов

        Returns:
            Dict[str, Any]: Готовая статистика согласно JSON-схеме ТЗ

        Examples:
            >>> composer = StatisticsComposer()
            >>> stats = composer.compose(accumulator, 1000)
            >>> stats.keys()
            ['totalRequestsCount', 'responseSizeInBytes', 'resources', ...]

        """
        return {
            "totalRequestsCount": total_requests,
            "responseSizeInBytes": self._compose_size_statistics(
                data_accumulator["response_sizes"]
            ),
            "resources": self._compose_resources(
                data_accumulator["resource_frequency"]
            ),
            "responseCodes": self._compose_response_codes(
                data_accumulator["status_frequency"]
            ),
            "requestsPerDate": self._compose_date_distribution(
                data_accumulator["date_distribution"], total_requests
            ),
            "uniqueProtocols": self._compose_unique_protocols(
                data_accumulator["unique_protocols"]
            ),
        }

    def _compose_size_statistics(self, sizes: list[int]) -> dict[str, int]:
        """Компонует статистику размеров ответов."""
        return self.size_calculator.calculate(sizes)

    def _compose_resources(self, resource_frequency: Counter) -> list[dict[str, Any]]:
        """Компонует топ-10 ресурсов."""
        return [
            {"resource": resource, "totalRequestsCount": count}
            for resource, count in resource_frequency.most_common(10)
        ]

    def _compose_response_codes(
        self, status_frequency: Counter
    ) -> list[dict[str, Any]]:
        """Компонует статистику HTTP-кодов ответов."""
        return [
            {"code": code, "totalResponsesCount": count}
            for code, count in sorted(status_frequency.items())  # Сортировка по коду
        ]

    def _compose_date_distribution(
        self, date_distribution: dict[str, int], total_requests: int
    ) -> list[dict[str, Any]]:
        """Компонует распределение запросов по датам."""
        result = []
        for date_str, count in sorted(date_distribution.items()):  # Сортировка по дате
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            result.append(
                {
                    "date": date_str,  # ISO8601 формат
                    "weekday": date_obj.strftime("%A"),  # Локализованное имя дня недели
                    "totalRequestsCount": count,
                    "totalRequestsPercentage": round(
                        (count / total_requests) * 100, 2
                    ),  # Точность 2 знака
                }
            )

        return result

    def _compose_unique_protocols(self, protocol_set: set) -> list[str]:
        """Компонует список уникальных протоколов."""
        return sorted(protocol_set)
