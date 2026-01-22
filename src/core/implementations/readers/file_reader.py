"""Реализация читателя локальных файлов."""

import glob
from collections.abc import Iterator
from pathlib import Path

from src.core.abstractions.readers import IFileReader
from src.domain.validators.file_format_validator import FileFormatValidator


class LocalFileReader(IFileReader):
    """Реализация IFileReader для чтения локальных файлов."""

    def __init__(self) -> None:
        self.format_validator = FileFormatValidator()

    def read_files(self, path_pattern: str) -> Iterator[str]:
        """Читает файлы по конкретному пути или шаблону glob."""
        # Оставляем glob.glob для совместимости
        file_paths = glob.glob(path_pattern)

        if not file_paths:
            msg = f"Файл(ы) '{path_pattern}' не найден(ы)"
            raise FileNotFoundError(msg)

        for file_path in file_paths:
            file_path_obj = Path(file_path)

            # Проверка что это файл через Path
            if not file_path_obj.is_file():
                msg = f"'{file_path}' не является файлом"
                raise ValueError(msg)

            # Валидация формата через FileFormatValidator
            self.format_validator.validate_extension(file_path)

            yield from self._read_single_file(file_path_obj)

    def _read_single_file(self, file_path: Path) -> Iterator[str]:
        """Читает один файл построчно."""
        try:
            with file_path.open(encoding="utf-8") as file:
                for line in file:
                    yield line.strip()
        except UnicodeDecodeError:
            with file_path.open(encoding="latin-1") as file:
                for line in file:
                    yield line.strip()
        except PermissionError as e:
            msg = f"Нет прав для чтения файла {file_path}"
            raise PermissionError(msg) from e
