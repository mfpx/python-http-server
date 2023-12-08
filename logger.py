# Logging
import logging
import logging.handlers
# Date and time formatting
from datetime import datetime
# Coloured text support - mainly for readabilty
from termcolor import colored

class CustomFormatter(logging.Formatter):

    def set_colour_mode(self, is_colour: bool) -> None:
        self.is_colour = is_colour

    def format(self, record: logging.LogRecord) -> str:
        if self.is_colour:
            log_message = f"[{self.__asctime(record, '%c')}] [{self.__colour_level(record)}]: {record.getMessage()}"
        else:
            log_message = f"[{self.__asctime(record, '%c')}] [{record.levelname}]: {record.getMessage()}"
        return log_message

    def __asctime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        dt = datetime.fromtimestamp(record.created)
        return dt.strftime(datefmt)

    def __colour_level(self, record: logging.LogRecord) -> str:
        if record.levelno == logging.DEBUG:
            return colored(record.levelname, "blue")
        elif record.levelno == logging.INFO:
            return colored(record.levelname, "green")
        elif record.levelno == logging.WARNING:
            return colored(record.levelname, "yellow")
        elif record.levelno == logging.ERROR:
            return colored(record.levelname, "red")
        elif record.levelno == logging.CRITICAL:
            return colored(record.levelname, "magenta")
        else:
            return colored(record.levelname, "white")

    def formatException(self, ei: tuple) -> str:
        return f"{colored(ei[0], 'red')}: {ei[1]}"

class Logger:

    def __call__(self) -> None:
        raise RuntimeError(f"Do not call {self.__name__} directly")

    def __init__(self, server_config_dict: dict) -> None:
        self.logger_config = self.__make_logger_config(server_config_dict)

    def __make_logger_config(self, config: dict) -> None:
        values = ["logfile_maxsize", "logfile_unit", "logfile", "logging_level", "logging"]
        out_dict = {}
        for value in values:
            out_dict[value] = config[value]
        return out_dict

    def __unit_conversion(self, in_unit: str, in_unit_value: int, out_unit: str) -> int:
        # Check if passed in types are correct
        if not isinstance(in_unit_value, int):
            raise TypeError("in_unit_value must be an integer")
        if not isinstance(out_unit, str):
            raise TypeError("out_unit must be a string")
        if not isinstance(in_unit, str):
            raise TypeError("in_unit must be a string")
        
        # Function to convert units
        if in_unit == "bytes" and out_unit == "kilobytes":
            return in_unit_value / 1024
        elif in_unit == "bytes" and out_unit == "megabytes":
            return in_unit_value / 1024 / 1024
        elif in_unit == "bytes" and out_unit == "gigabytes":
            return in_unit_value / 1024 / 1024 / 1024
        elif in_unit == "kilobytes" and out_unit == "bytes":
            return in_unit_value * 1024
        elif in_unit == "megabytes" and out_unit == "bytes":
            return in_unit_value * 1024 * 1024
        elif in_unit == "gigabytes" and out_unit == "bytes":
            return in_unit_value * 1024 * 1024 * 1024
        elif in_unit == out_unit:
            return in_unit_value
        else:
            return 0

    def logging_init(self) -> logging.Logger:
        # Coloured formatter
        coloured_formatter = CustomFormatter()
        coloured_formatter.set_colour_mode(True)

        # Uncoloured formatter
        uncoloured_formatter = CustomFormatter()
        uncoloured_formatter.set_colour_mode(False)

        # Setup logging
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(coloured_formatter)
        file_handler = logging.handlers.RotatingFileHandler(
            self.logger_config["logfile"],
            'a',
            self.__unit_conversion(
                self.logger_config["logfile_unit"],
                self.logger_config["logfile_maxsize"],
                'bytes'),
            5)
        file_handler.setFormatter(uncoloured_formatter)

        if self.logger_config["logging"]:
            handlers = [
                file_handler,
                stream_handler
            ]
        else:
            # If logging is disabled, only log to stdout
            handlers = [stream_handler]

        logging.basicConfig(
            level=self.logger_config["logging_level"].upper(),
            handlers=handlers)
        logging.info("Logging init complete")
        return logging.getLogger("ServerLogger")