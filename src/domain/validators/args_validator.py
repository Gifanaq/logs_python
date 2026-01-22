from argparse import Namespace
from datetime import datetime


class ArgsValidator:
    """Валидатор аргументов командной строки."""

    @staticmethod
    def validate_args(args: Namespace) -> None:
        """Валидирует аргументы командной строки."""
        if args.date_from:
            datetime.fromisoformat(args.date_from)
        if args.date_to:
            datetime.fromisoformat(args.date_to)
        if args.date_from and args.date_to and args.date_from >= args.date_to:
            msg = "Дата 'from' должна быть меньше даты 'to'"
            raise ValueError(msg)
