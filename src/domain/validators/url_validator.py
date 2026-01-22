"""Валидатор URL.

Отвечает ТОЛЬКО за валидацию URL.
"""

from urllib.parse import urlparse


class UrlValidator:
    """Валидатор URL с единственной ответственностью."""

    @staticmethod
    def _validate_scheme(scheme: str) -> None:
        """Валидирует схему URL."""
        if scheme not in ["http", "https"]:
            msg = f"Неподдерживаемая схема: {scheme}. Поддерживаются: http, https"
            raise ValueError(msg)

    @staticmethod
    def _validate_url_structure(url: str) -> None:
        """Валидирует базовую структуру URL."""
        if not url:
            msg = "URL не может быть пустым"
            raise ValueError(msg)

        if not isinstance(url, str):
            msg = "URL должен быть строкой"
            raise TypeError(msg)

    @staticmethod
    def _validate_url_components(result: object) -> None:
        """Валидирует компоненты распарсенного URL."""
        if not result.scheme:
            msg = "URL должен содержать схему (http:// или https://)"
            raise ValueError(msg)

        if not result.netloc:
            msg = "URL должен содержать домен"
            raise ValueError(msg)

        UrlValidator._validate_scheme(result.scheme)

    @staticmethod
    def validate(url: str) -> None:
        """Валидирует URL.

        Args:
            url: URL для валидации

        Raises:
            ValueError: Если URL некорректен

        """
        try:
            UrlValidator._validate_url_structure(url)
            result = urlparse(url)
            UrlValidator._validate_url_components(result)
        except ValueError:
            # Перевыбрасываем наши кастомные ValueError как есть
            raise
        except Exception as e:
            # Оборачиваем все остальные исключения
            msg = f"Некорректный URL: {url}"
            raise ValueError(msg) from e

    @staticmethod
    def is_valid(url: str) -> bool:
        """Проверяет валидность URL без выбрасывания исключений.

        Returns:
            bool: True если URL валиден

        """
        try:
            UrlValidator.validate(url)
        except ValueError:
            return False
        else:
            return True
