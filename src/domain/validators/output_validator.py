import os
from pathlib import Path

from src.core.abstractions.formatters import IReportFormatter


class OutputValidator:
    """Валидатор выходных файлов.

    Ответственность:
    - Валидация пути выходного файла
    - Проверка соответствия расширения формату
    - Проверка прав доступа и существования файла
    """

    @staticmethod
    def validate_output_path(output_path: str, formatter: IReportFormatter) -> None:
        """Валидирует путь выходного файла."""
        # Преобразуем в Path объект
        output_path_obj = Path(output_path)
        expected_extension = formatter.get_file_extension()

        # Проверка расширения
        if output_path_obj.suffix != expected_extension:
            msg = (
                f"Неверное расширение: '{output_path}'. "
                f"Ожидается: '{expected_extension}'"
            )

            raise ValueError(msg)

        # Проверка существования файла
        if output_path_obj.exists():
            msg = f"Файл уже существует: '{output_path}'"
            raise ValueError(msg)

        # Получаем директорию (родительскую папку)
        if output_path_obj.parent == Path():
            output_dir = Path.cwd()
        else:
            output_dir = output_path_obj.parent
        # Проверка существования директории
        if not output_dir.is_dir():
            msg = f"Директория не существует: '{output_dir}'"
            raise ValueError(msg)

        # Проверка прав на запись
        if not os.access(output_dir, os.W_OK):
            msg = f"Нет прав на запись: '{output_dir}'"
            raise ValueError(msg)
