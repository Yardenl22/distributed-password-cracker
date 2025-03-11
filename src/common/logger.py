import logging
import os
from typing import Any


class CustomLogger(logging.Logger):
    def __init__(self, name: str = "logger", level: int = logging.INFO, log_file: str = "logs/app.log"):
        super().__init__(name, level)

        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        self.addHandler(console_handler)
        self.addHandler(file_handler)

    def info(self, message: str, **metadata: Any):
        if metadata:
            message += f" | Metadata: {metadata}"
        super().info(message)

    def error(self, message: str, **metadata: Any):
        if metadata:
            message += f" | Metadata: {metadata}"
        super().error(message)

    def warning(self, message: str, **metadata: Any):
        if metadata:
            message += f" | Metadata: {metadata}"
        super().warning(message)

    def debug(self, msg: str, **metadata: Any):
        if metadata:
            msg += f" | Metadata: {metadata}"
        super().debug(msg)


logger = CustomLogger()
