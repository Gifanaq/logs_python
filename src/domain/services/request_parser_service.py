"""Сервис для извлечения структурированных данных из HTTP-запросов.

Отвечает ТОЛЬКО за парсинг request строки логов NGINX.
"""


class RequestParserService:
    """Извлекает метод, ресурс и протокол из HTTP-запросов.

    Не зависит от формата логов или бизнес-логики статистики.
    """

    # Константы для минимального количества частей в запросе
    min_parts_for_method = 1
    min_parts_for_resource = 2
    min_parts_for_protocol = 3

    # Константы для значений по умолчанию
    default_resource = "/"
    default_protocol = "UNKNOWN"
    default_method = "UNKNOWN"

    @staticmethod
    def extract_resource(request: str) -> str:
        """Извлекает путь ресурса из HTTP-запроса.

        Args:
            request: Строка запроса из лога NGINX

        Returns:
            str: Путь ресурса или "/" если не удалось извлечь

        Examples:
            "GET /downloads/product_1 HTTP/1.1" → "/downloads/product_1"
            "POST /api/users HTTP/2.0" → "/api/users"
            "INVALID" → "/"

        """
        if not request:
            return RequestParserService.default_resource

        parts = request.strip().split()
        return (
            parts[1]
            if len(parts) >= RequestParserService.min_parts_for_resource
            else RequestParserService.default_resource
        )

    @staticmethod
    def extract_protocol(request: str) -> str:
        """Извлекает протокол из HTTP-запроса.

        Args:
            request: Строка запроса из лога NGINX

        Returns:
            str: Протокол или "UNKNOWN" если не удалось извлечь

        Examples:
            "GET /downloads/product_1 HTTP/1.1" → "HTTP/1.1"
            "POST /api/users HTTP/2" → "HTTP/2"
            "INVALID" → "UNKNOWN"

        """
        if not request:
            return RequestParserService.default_protocol

        parts = request.strip().split()
        return (
            parts[2]
            if len(parts) >= RequestParserService.min_parts_for_protocol
            else RequestParserService.default_protocol
        )

    @staticmethod
    def extract_method(request: str) -> str:
        """Извлекает HTTP-метод из запроса.

        Args:
            request: Строка запроса из лога NGINX

        Returns:
            str: HTTP-метод или "UNKNOWN" если не удалось извлечь

        Examples:
            "GET /downloads/product_1 HTTP/1.1" → "GET"
            "POST /api/users HTTP/2.0" → "POST"
            "INVALID" → "UNKNOWN"

        """
        if not request:
            return RequestParserService.default_method

        parts = request.strip().split()
        return (
            parts[0]
            if len(parts) >= RequestParserService.min_parts_for_method
            else RequestParserService.default_method
        )
