"""Фабрика для создания LogAnalyzerService.

Собирает все зависимости для анализа логов.
"""

from src.core.implementations.calculators.nginx_statistics_calculator import (
    NginxStatisticsCalculator,
)
from src.core.implementations.parsers.log_parser import NginxLogParser
from src.domain.services.log_analyze_service import LogAnalyzerService
from src.infrastructure.factories.formatter_factory import FormatterFactory
from src.infrastructure.factories.reader_factory import ReaderFactory


class LogAnalyzerFactory:
    """Фабрика для создания LogAnalyzerService.

    Ответственность:
    - Сбор всех зависимостей для LogAnalyzerService
    - Инкапсуляция сложности создания сервиса
    - Гарантия правильной настройки зависимостей
    """

    @staticmethod
    def create() -> LogAnalyzerService:
        """Создает готовый к работе LogAnalyzerService.

        Returns:
            LogAnalyzerService: Сервис со всеми зависимостями

        """
        reader_factory = ReaderFactory()
        parser = NginxLogParser()
        calculator = NginxStatisticsCalculator()
        formatter_factory = FormatterFactory()

        return LogAnalyzerService(
            reader_factory=reader_factory,
            parser=parser,
            calculator=calculator,
            formatter_factory=formatter_factory,
        )
