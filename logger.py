import logging
import logging.handlers

class Logger:

    def __call__(self) -> None:
        raise RuntimeError(f'Do not call {self.__name__} directly')

    def __init__(self, server_config_dict: dict) -> None:
        self.logger_config = self.__make_logger_config(server_config_dict)

    def __make_logger_config(self, config: dict) -> None:
        values = ['logfile_maxsize', 'logfile_unit', 'logfile', 'logging_level', 'logging']
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
        if self.logger_config["logging"]:
            handlers = [
                logging.handlers.RotatingFileHandler(
                    self.logger_config["logfile"],
                    'a',
                    self.__unit_conversion(
                        self.logger_config["logfile_unit"],
                        self.logger_config["logfile_maxsize"],
                        'bytes'),
                    5),
                logging.StreamHandler()]
        else:
            handlers = [logging.StreamHandler()]

        logging.basicConfig(
            level=self.logger_config["logging_level"].upper(),
            format='[%(asctime)s] [%(levelname)s]: %(message)s',
            datefmt='%c',
            handlers=handlers)
        logging.info("Logging init complete")
        return logging.getLogger("ServerLogger")