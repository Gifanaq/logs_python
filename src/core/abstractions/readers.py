"""Абстракции для чтения данных."""

from abc import ABC, abstractmethod
from collections.abc import Iterator


class IFileReader(ABC):
    """Базовый интерфейс для всех читателей файлов."""

    @abstractmethod
    def read_files(self, path_pattern: str) -> Iterator[str]:
        """Читает файлы и возвращает итератор строк.

        Args:
            path_pattern: Путь к файлу, шаблон glob или URL

        Returns:
            Iterator[str]: Построчный итератор содержимого файлов

        Raises:
            FileNotFoundError: Если файлы не найдены
            ValueError: Если неподдерживаемый формат или путь
            requests.RequestException: Если ошибка загрузки по URL

        """
