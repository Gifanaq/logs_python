"""Фабрика для создания ридеров файлов.

Отвечает за выбор правильной реализации IFileReader на основе пути.
"""

from src.core.abstractions.readers import IFileReader
from src.core.implementations.readers.file_reader import LocalFileReader
from src.core.implementations.readers.url_reader import UrlReader
from src.domain.validators.url_validator import UrlValidator


class ReaderFactory:
    """Фабрика для создания ридеров файлов.

    Ответственность:
    - Анализ пути (локальный файл vs URL)
    - Создание соответствующей реализации IFileReader
    - Инкапсуляция логики выбора ридера

    Не знает о:
    - Бизнес-логике анализа логов
    - Форматах вывода
    - Парсерах или калькуляторах
    """

    @staticmethod
    def create_reader(path: str) -> IFileReader:
        """Создает ридер на основе анализа пути.

        Args:
            path: Путь к файлу (локальный, шаблон glob или URL)

        Returns:
            IFileReader: Соответствующая реализация ридера

        Examples:
            >>> ReaderFactory.create_reader("/var/log/nginx/access.log")
            LocalFileReader()

            >>> ReaderFactory.create_reader("https://example.com/logs/access.log")
            UrlReader()

            >>> ReaderFactory.create_reader("logs/*.log")
            LocalFileReader()

        """
        if not path:
            msg = "Path cannot be empty or None"
            raise ValueError(msg)

        # Используем UrlValidator для определения типа пути
        if UrlValidator.is_valid(path):
            return UrlReader()
        return LocalFileReader()
