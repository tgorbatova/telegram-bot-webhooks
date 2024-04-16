import sys

from typing import Literal

import loguru

from dataclasses import asdict, dataclass


@dataclass
class MessageExtras:
    action: str | None = None
    uid: int | str | None = None
    username: str | None = None


def format_plain(record: "loguru.Record") -> str:
    """Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.
    """
    extra = MessageExtras(**record["extra"])
    record.update(asdict(extra))  # type: ignore
    if record["level"].name in {"INFO", "SUCCESS"}:
        message_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan> |"
            " {extra} | <level>{message}</level>\n"
        )
    else:
        message_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
            "| {extra} | <level>{message}</level>\n"
        )

    return message_format


LogLevel = Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]


def init_logging(
    json_logging: bool = True,
    rotation: str = "1 week",
    json_log_level: LogLevel = "INFO",
    plain_log_level: LogLevel = "INFO",
    logs_dir: str = "log",
) -> None:
    """Replaces logging handlers with a handler for using the custom handler."""

    handlers = [
        {
            "sink": sys.stdout,
            "level": plain_log_level,
            "format": format_plain,
            "colorize": True,
        }
    ]

    if json_logging:
        handlers.append(
            {
                "sink": f"{logs_dir}/logs.log",  # type: ignore[dict-item]
                "level": json_log_level,
                "serialize": True,
                "rotation": rotation,  # type: ignore[dict-item]
            },
        )
    loguru.logger.configure(handlers=handlers)
    loguru.logger.info(
        f"Logs inited. {json_logging=} {rotation=} {json_log_level=} {plain_log_level=} {logs_dir=}"
    )
