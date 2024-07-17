import logging
import traceback

import colorlog
import telebot


class CustomHandler(logging.Handler):
    def __init__(self):
        super().__init__()

        self.log_colors = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        self.formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(levelname)s] :%(reset)s %(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors=self.log_colors,
            reset=True  # Reset color after log level
        )

    def emit(self, record):
        log_entry = self.formatter.format(record)
        if record.levelno >= logging.ERROR:
            tb = traceback.format_exc()
            log_entry += f'\n{tb}'
        print(log_entry)


class TeleBotFilter(logging.Filter):
    def filter(self, record):
        return record.name == 'TeleBot'


def init_custom_logger(log_level):
    custom_handler = CustomHandler()
    custom_handler.setLevel(log_level)  # Set the desired log level
    telebot_logger = telebot.logger
    for handler in telebot_logger.handlers[:]:
        telebot_logger.removeHandler(handler)
    logging.getLogger().addHandler(custom_handler)
    telebot_logger.addFilter(TeleBotFilter())

# def get_logger(logger_name):
