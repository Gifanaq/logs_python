from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class LogEntry:
    """Неизменяемая модель данных лога NGINX.

    Отвечает ТОЛЬКО за хранение данных.
    """

    remote_addr: str
    remote_user: None | str
    time_local: datetime
    request: str
    status: int
    body_bytes_sent: int
    http_referer: str
    http_user_agent: str
