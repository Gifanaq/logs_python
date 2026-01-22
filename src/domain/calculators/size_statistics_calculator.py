"""Вспомогательный калькулятор для статистики размеров ответов.

С умным переключением между точным и приближенным расчетом.
"""

import random

import numpy as np


class SizeStatisticsCalculator:
    """Умный калькулятор статистики размеров.

    Автоматически выбирает метод расчета для баланса точности и памяти.
    """

    def __init__(self, exact_threshold: int = 100000) -> None:
        """exact_threshold: Переключение на приближенный расчет."""
        self.exact_threshold = exact_threshold

    def calculate(self, sizes: list[int]) -> dict[str, float]:
        """Рассчитывает статистику размеров с умным выбором алгоритма.

        Правило:
        - До 100k записей: точный расчет (numpy.percentile)
        - Свыше 100k: приближенный расчет (reservoir sampling)
        """
        if not sizes:
            return self._get_empty_stats()

        # Базовые метрики (всегда точные)
        total = sum(sizes)
        max_size = max(sizes)
        avg = round(total / len(sizes), 2)

        # Умный выбор метода для p95
        if len(sizes) <= self.exact_threshold:
            # Мало данных → ТОЧНЫЙ расчет
            p95 = self._calculate_exact_percentile(sizes)
        else:
            # Много данных → ПРИБЛИЖЕННЫЙ расчет
            p95 = self._calculate_approx_percentile(sizes)

        return {"average": float(avg), "max": float(max_size), "p95": p95}

    def _calculate_exact_percentile(self, sizes: list[int]) -> float:
        """Точный расчет 95-го перцентиля используя numpy."""
        return float(round(np.percentile(sizes, 95), 2))

    def _calculate_approx_percentile(self, sizes: list[int]) -> float:
        """Приближенный расчет 95-го перцентиля используя reservoir sampling."""
        sample = self._reservoir_sample(sizes, sample_size=10000)
        return float(round(np.percentile(sample, 95), 2))

    def _reservoir_sample(self, data: list[int], sample_size: int) -> list[int]:
        """Reservoir sampling для случайной выборки."""
        if len(data) <= sample_size:
            return data.copy()

        reservoir = data[:sample_size]

        for i in range(sample_size, len(data)):
            j = random.randint(0, i)
            if j < sample_size:
                reservoir[j] = data[i]

        return reservoir

    def _get_empty_stats(self) -> dict[str, float]:
        """Возвращает структуру пустой статистики."""
        return {"average": 0.0, "max": 0.0, "p95": 0.0}
