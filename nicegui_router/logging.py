import logging


class LogColors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname == "INFO":
            record.levelname = f"{LogColors.GREEN}{levelname}{LogColors.RESET}"
        elif levelname == "WARNING":
            record.levelname = f"{LogColors.YELLOW}{levelname}{LogColors.RESET}"
        elif levelname == "ERROR":
            record.levelname = f"{LogColors.RED}{levelname}{LogColors.RESET}"
        elif levelname == "DEBUG":
            record.levelname = f"{LogColors.CYAN}{levelname}{LogColors.RESET}"
        record.msg = f"{LogColors.BLUE}{record.msg}{LogColors.RESET}"
        return super().format(record)


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = ColoredFormatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    # Prevent the logger from propagating to the root logger
    logger.propagate = False
    return logger
