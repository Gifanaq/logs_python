import json
from typing import Any

from src.core.abstractions.formatters import IReportFormatter


class JsonFormatter(IReportFormatter):
    """Форматирует статистику в JSON формат.

    Ответственность:
    - Преобразование статистики в отформатированную JSON строку
    - Гарантия читаемости (отступы, Unicode)
    - Соблюдение JSON-схемы из ТЗ

    Не знает о:
    - Источнике данных
    - Других форматах вывода
    - Логике расчета статистики
    """

    def format(self, statistics: dict[str, Any]) -> str:
        """Форматирует статистику в красивый JSON.

        Args:
            statistics: Статистика в формате JSON-схемы ТЗ

        Returns:
            str: Отформатированная JSON строка с отступами

        Examples:
            >>> formatter = JsonFormatter()
            >>> json_output = formatter.format({"total": 1000})
            >>> print(json_output)
            {
              "total": 1000
            }

        """
        return json.dumps(
            statistics,
            indent=2,  # Читаемые отступы
            ensure_ascii=False,  # Поддержка Unicode (кириллица)
            sort_keys=True,  # Предсказуемый порядок ключей
        )

    def get_file_extension(self) -> str:
        """Возвращает расширение для JSON файлов.

        Returns:
            str: Расширение '.json'

        """
        return ".json"
