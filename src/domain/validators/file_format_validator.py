"""Валидатор форматов файлов.

Отвечает ТОЛЬКО за валидацию форматов файлов.
"""

from pathlib import Path


class FileFormatValidator:
    """Валидатор форматов файлов с единственной ответственностью."""

    def __init__(
        self, supported_extensions: tuple[str, ...] = (".log", ".txt")
    ) -> None:
        self.supported_extensions = supported_extensions

    def validate_extension(self, filename: str) -> None:
        """Валидирует расширение файла.

        Args:
            filename: Имя файла или URL для проверки

        Raises:
            ValueError: Если формат не поддерживается

        """
        if not filename:
            msg = "Имя файла не может быть пустым"
            raise ValueError(msg)

        if filename.startswith(("http://", "https://")):
            return  # ← URL могут не иметь расширения!

        ext = Path(filename).suffix.lower()

        if ext not in self.supported_extensions:
            msg = (
                f"Неподдерживаемый формат файла: {filename}. "
                f"Поддерживаются: {', '.join(self.supported_extensions)}"
            )
            raise ValueError(msg)

    def validate_content_type(self, content_type: str) -> None:
        """Валидирует Content-Type HTTP заголовка.

        Args:
            content_type: Значение заголовка Content-Type

        Raises:
            ValueError: Если Content-Type не поддерживается

        """
        if not content_type:
            # Если Content-Type не указан, считаем валидным
            return

        content_type = content_type.lower()
        supported_types = ["text/plain", "application/octet-stream"]

        if not any(supported in content_type for supported in supported_types):
            msg = f"Неподдерживаемый Content-Type: {content_type}"
            raise ValueError(msg)

    def is_supported_extension(self, filename: str) -> bool:
        """Проверяет поддерживаемое расширение без выбрасывания исключений.

        Returns:
            bool: True если расширение поддерживается

        """
        try:
            self.validate_extension(filename)
        except ValueError:
            return False
        else:
            return True
