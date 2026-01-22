from pathlib import Path


class ReportSaver:
    """Сервис сохранения отчетов в файлы.

    Ответственность:
    - Сохранение текста в файл с правильной кодировкой
    - Создание директорий при необходимости
    """

    @staticmethod
    def save_report(report: str, output_path: str) -> None:
        """Сохраняет отчет в файл.

        Args:
            report: Текст отчета для сохранения
            output_path: Путь к файлу для сохранения

        Raises:
            OSError: Если произошла ошибка при записи файла

        """
        output_path_obj = Path(output_path)
        output_dir = output_path_obj.parent

        # Создаем директорию если нужно
        output_dir.mkdir(parents=True, exist_ok=True)

        # Сохраняем отчет в файл
        with output_path_obj.open("w", encoding="utf-8") as file:
            file.write(report)
