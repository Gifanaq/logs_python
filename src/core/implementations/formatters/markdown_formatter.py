from typing import Any

from src.core.abstractions.formatters import IReportFormatter


class MarkdownFormatter(IReportFormatter):
    """Форматирует статистику в Markdown формат с таблицами.

    Ответственность:
    - Преобразование статистики в человеко-читаемый Markdown
    - Построение красивых таблиц с динамической шириной колонок
    - Форматирование чисел и дат для читаемости

    Не знает о:
    - Источнике данных
    - Других форматах вывода
    - Логике расчета статистики
    """

    def format(self, statistics: dict[str, Any]) -> str:
        """Форматирует статистику в Markdown отчет.

        Args:
            statistics: Статистика в формате JSON-схемы ТЗ

        Returns:
            str: Отформатированный Markdown отчет

        """
        sections = []

        # 1. Общая информация
        sections.append(self._format_general_info(statistics))

        # 2. Запрашиваемые ресурсы
        sections.append(self._format_resources(statistics.get("resources", [])))

        # 3. Коды ответа
        sections.append(
            self._format_response_codes(statistics.get("responseCodes", []))
        )

        # 4. Распределение по датам (доп. баллы)
        if statistics.get("requestsPerDate"):
            sections.append(
                self._format_requests_per_date(statistics["requestsPerDate"])
            )

        # 5. Уникальные протоколы (доп. баллы)
        if statistics.get("uniqueProtocols"):
            sections.append(
                self._format_unique_protocols(statistics["uniqueProtocols"])
            )

        return "\n\n".join(sections)

    def _format_general_info(self, stats: dict[str, Any]) -> str:
        """Форматирует раздел общей информации."""
        size_info = stats.get("responseSizeInBytes", {})

        table_data = [
            ("Файл(-ы)", f"`{stats['files'][0]}`" if stats.get("files") else "-"),
            (
                "Количество запросов",
                self._format_number(stats.get("totalRequestsCount", 0)),
            ),
            (
                "Средний размер ответа",
                f"{self._format_number(size_info.get('average', 0))}b",
            ),
            (
                "Максимальный размер ответа",
                f"{self._format_number(size_info.get('max', 0))}b",
            ),
            ("95p размера ответа", f"{self._format_number(size_info.get('p95', 0))}b"),
        ]

        return "#### Общая информация\n\n" + self._create_table(
            headers=["Метрика", "Значение"],
            data=table_data,
            alignments=[":---:", "---:"],
        )

    def _format_resources(self, resources: list[dict[str, Any]]) -> str:
        """Форматирует топ ресурсов."""
        if not resources:
            return "#### Запрашиваемые ресурсы\n\n*Нет данных*"

        table_data = [
            (resource["resource"], self._format_number(resource["totalRequestsCount"]))
            for resource in resources[:10]
        ]

        return "#### Запрашиваемые ресурсы\n\n" + self._create_table(
            headers=["Ресурс", "Количество"],
            data=table_data,
            alignments=[":---:", "---:"],
        )

    def _format_response_codes(self, response_codes: list[dict[str, Any]]) -> str:
        """Форматирует коды ответа."""
        if not response_codes:
            return "#### Коды ответа\n\n*Нет данных*"

        table_data = []
        for code_info in response_codes:
            code = code_info["code"]
            count = code_info["totalResponsesCount"]
            name = self._get_http_status_name(code)
            table_data.append((str(code), name, self._format_number(count)))

        return "#### Коды ответа\n\n" + self._create_table(
            headers=["Код", "Имя", "Количество"],
            data=table_data,
            alignments=[":---:", ":---:", "---:"],
        )

    def _format_requests_per_date(self, requests_per_date: list[dict[str, Any]]) -> str:
        """Форматирует распределение по датам (доп. баллы)."""
        table_data = [
            (
                item["date"],
                item["weekday"],
                self._format_number(item["totalRequestsCount"]),
                f"{item['totalRequestsPercentage']}%",
            )
            for item in requests_per_date
        ]

        return "#### Распределение запросов по датам\n\n" + self._create_table(
            headers=["Дата", "День недели", "Количество", "Процент"],
            data=table_data,
            alignments=[":---:", ":---:", "---:", "---:"],
        )

    def _format_unique_protocols(self, protocols: list[str]) -> str:
        """Форматирует уникальные протоколы (доп. баллы)."""
        protocols_text = ", ".join(f"`{proto}`" for proto in protocols)
        return f"#### Уникальные протоколы\n\n{protocols_text}"

    def _create_table(
        self, headers: list[str], data: list[tuple], alignments: list[str]
    ) -> str:
        """Создает Markdown таблицу с динамической шириной колонок."""
        if not data:
            return ""

        # 1. Рассчитываем максимальную ширину для каждой колонки
        col_widths = []
        for i in range(len(headers)):
            # Максимальная ширина = max(длина заголовка, max(длина данных в колонке))
            header_width = len(headers[i])
            data_width = max(len(str(row[i])) for row in data)
            col_widths.append(max(header_width, data_width, 5))  # минимум 5 символов

        lines = []

        # 2. Заголовок с динамической шириной
        header_line = "|"
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]}} |"
        lines.append(header_line)

        # 3. Разделитель с динамической шириной
        separator_line = "|"
        for i, alignment in enumerate(alignments):
            width = col_widths[i]
            if alignment == ":---:":
                separator_line += f" :{'-'*(width-2)}: |"  # Центр
            elif alignment == "---:":
                separator_line += f" {'-'*(width-1)}: |"  # Право
            else:
                separator_line += f" {'-'*(width)} |"  # Лево
        lines.append(separator_line)

        # 4. Данные с динамической шириной
        for row in data:
            data_line = "|"
            for i, cell in enumerate(row):
                cell_str = str(cell)
                if alignments[i] == "---:":
                    data_line += f" {cell_str:>{col_widths[i]}} |"  # Право для чисел
                else:
                    data_line += f" {cell_str:<{col_widths[i]}} |"  # Лево для текста
            lines.append(data_line)

        return "\n".join(lines)

    def _format_number(self, number: int) -> str:
        """Форматирует число с разделителями тысяч."""
        return f"{number:,}".replace(",", "_")

    def _get_http_status_name(self, code: int) -> str:
        """Возвращает человеко-читаемое имя HTTP статуса."""
        status_names = {
            # 1xx: Informational
            100: "Continue",
            101: "Switching Protocols",
            102: "Processing",
            103: "Early Hints",
            # 2xx: Success
            200: "OK",
            201: "Created",
            202: "Accepted",
            203: "Non-Authoritative Information",
            204: "No Content",
            205: "Reset Content",
            206: "Partial Content",
            207: "Multi-Status",
            208: "Already Reported",
            226: "IM Used",
            # 3xx: Redirection
            300: "Multiple Choices",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            305: "Use Proxy",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            # 4xx: Client Errors
            400: "Bad Request",
            401: "Unauthorized",
            402: "Payment Required",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            407: "Proxy Authentication Required",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            412: "Precondition Failed",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            416: "Range Not Satisfiable",
            417: "Expectation Failed",
            418: "I'm a teapot",
            421: "Misdirected Request",
            422: "Unprocessable Entity",
            423: "Locked",
            424: "Failed Dependency",
            425: "Too Early",
            426: "Upgrade Required",
            428: "Precondition Required",
            429: "Too Many Requests",
            431: "Request Header Fields Too Large",
            451: "Unavailable For Legal Reasons",
            # 5xx: Server Errors
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported",
            506: "Variant Also Negotiates",
            507: "Insufficient Storage",
            508: "Loop Detected",
            510: "Not Extended",
            511: "Network Authentication Required",
        }
        return status_names.get(code, f"HTTP {code}")

    def get_file_extension(self) -> str:
        """Возвращает расширение для Markdown файлов."""
        return ".md"
