"""Главный калькулятор статистики NGINX.

Фасад/Координатор для расчета полной статистики логов.

Архитектурная роль:
- Предоставляет простой интерфейс для сложной системы расчетов
- Координирует workflow между специализированными компонентами
- Инкапсулирует сложность бизнес-процесса
"""

import logging
from typing import Any

from src.core.abstractions.calculators import IStatisticsCalculator
from src.domain.accumulators.data_accumulator import DataAccumulator
from src.domain.calculators.size_statistics_calculator import SizeStatisticsCalculator
from src.domain.composers.statistics_composer import StatisticsComposer
from src.domain.services.request_parser_service import RequestParserService
from src.models.log_entry import LogEntry

logger = logging.getLogger(__name__)


class NginxStatisticsCalculator(IStatisticsCalculator):
    """Фасад для расчета полной статистики логов NGINX.

    Ответственность:
    - Координация процесса: сбор данных → компоновка статистики
    - Логирование ключевых этапов выполнения
    - Обработка граничных случаев (пустые данные, ошибки)
    - Предоставление простого интерфейса для сложной системы

    Не знает о:
    - Алгоритмах сбора данных (знает DataAccumulator)
    - Математике расчетов (знает SizeStatisticsCalculator)
    - Структуре JSON результата (знает StatisticsComposer)
    """

    def __init__(self) -> None:
        """Инициализация компонентов системы."""
        self.request_parser = RequestParserService()
        self.size_calculator = SizeStatisticsCalculator()
        self.data_accumulator = DataAccumulator(self.request_parser)
        self.statistics_composer = StatisticsComposer(self.size_calculator)

    def calculate(self, entries: list[LogEntry]) -> dict[str, Any]:
        """Рассчитывает полную статистику по логам NGINX.

        Args:
            entries: Валидированные записи логов от парсера

        Returns:
            Dict[str, Any]: Полная статистика согласно JSON-схеме ТЗ

        Raises:
            ValueError: Если entries is None
            Exception: Любая ошибка в процессе расчета

        Examples:
            >>> calculator = NginxStatisticsCalculator()
            >>> stats = calculator.calculate(log_entries)
            >>> print(stats["totalRequestsCount"])
            1000

        """
        # Валидация входных данных
        if entries is None:
            msg = "Entries cannot be None"
            raise ValueError(msg)

        if not entries:
            logger.info("Нет данных для расчета статистики")
            return self._get_empty_stats()

        logger.info(f"Запуск расчета статистики по {len(entries):,} записям")

        try:
            # Фаза 1: Сбор данных (однопроходная агрегация)
            accumulated_data = self.data_accumulator.accumulate(entries)

            # Фаза 2: Компоновка финальной статистики
            statistics = self.statistics_composer.compose(
                accumulated_data, len(entries)
            )

        except Exception:
            logger.exception("Ошибка в процессе расчета статистики")
            # Fail-fast: пробрасываем исключение дальше
            raise
        else:
            logger.info("Статистика успешно рассчитана")
            return statistics

    def _get_empty_stats(self) -> dict[str, Any]:
        """Возвращает структуру пустой статистики.

        Returns:
            Dict[str, Any]: Статистика с нулевыми значениями согласно JSON-схеме

        Notes:
            Гарантирует согласованность API даже при отсутствии данных

        """
        return {
            "totalRequestsCount": 0,
            "responseSizeInBytes": {"average": 0, "max": 0, "p95": 0},
            "resources": [],
            "responseCodes": [],
            "requestsPerDate": [],
            "uniqueProtocols": [],
        }
