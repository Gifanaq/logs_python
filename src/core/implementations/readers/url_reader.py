"""Реализация читателя URL с использованием requests."""

from collections.abc import Iterator

import requests

from src.core.abstractions.readers import IFileReader
from src.domain.validators.file_format_validator import FileFormatValidator
from src.domain.validators.url_validator import UrlValidator


class UrlReader(IFileReader):
    """Реализация IFileReader для чтения файлов по URL.

    Единственная ответственность: чтение данных по URL.
    """

    def __init__(self) -> None:
        self.url_validator = UrlValidator()
        self.format_validator = FileFormatValidator()

    def read_files(self, url: str) -> Iterator[str]:
        """Читает файл по URL.

        Делегирует валидацию специализированным классам.
        """
        # 1. Валидация URL
        self.url_validator.validate(url)

        # 2. Валидация расширения файла
        self.format_validator.validate_extension(url)

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # 3. Валидация Content-Type
            content_type = response.headers.get("Content-Type", "")
            self.format_validator.validate_content_type(content_type)

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    yield line.strip()

        except requests.exceptions.HTTPError as e:
            not_found_status = 404
            if e.response.status_code == not_found_status:
                msg = f"URL не найден (404): {url}"
                raise FileNotFoundError(msg) from e
            else:
                msg = f"Ошибка HTTP {e.response.status_code}: {url}"
                raise ValueError(msg) from e
        except requests.exceptions.RequestException as e:
            msg = f"Ошибка загрузки URL {url}: {e}"
            raise ValueError(msg) from e
