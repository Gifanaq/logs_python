import argparse
import logging
import sys

from src.domain.validators.args_validator import ArgsValidator
from src.infrastructure.factories.log_analyzer_factory import LogAnalyzerFactory

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Точка входа приложения."""
    try:
        args = parse_args()
        ArgsValidator.validate_args(args)  # ← Валидация в main
        analyzer = LogAnalyzerFactory.create()
        return analyzer.analyze(args)

    except (ValueError, FileNotFoundError):
        return 2
    except Exception:
        return 1


def parse_args() -> argparse.Namespace:
    """ТОЛЬКО парсинг аргументов."""
    parser = argparse.ArgumentParser(description="Анализатор логов NGINX")
    parser.add_argument("-p", "--path", required=True, help="Путь к лог-файлам")
    parser.add_argument(
        "-o", "--output", required=True, help="Путь для сохранения отчета"
    )
    parser.add_argument(
        "-f", "--format", required=True, choices=["json", "markdown", "adoc"]
    )
    parser.add_argument("--from", dest="date_from", default=None)
    parser.add_argument("--to", dest="date_to", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
