import sys
import time

CRITICAL: int = const(50)
ERROR = const(40)
WARNING = const(30)
INFO = const(20)
DEBUG = const(10)
NOTSET = const(0)

_level_str = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG"
}

_stream = sys.stderr  # default output
_filename: str = None  # overrides stream
_level: str = INFO  # ignore messages which are less severe
_format: str = "%(levelname)s:%(name)s:%(message)s"  # default message format
_format_asctime = False
_format_chrono = False
_loggers: {} = dict()


class Logger:

    def __init__(self, name):
        self.name = name
        self.level = _level
        self.start_ms = time.ticks_ms()

    def log(self, level, message, *args):
        if level < self.level:
            return

        try:
            if args:
                message = message % args

            record = dict()
            record["levelname"] = _level_str.get(level, str(level))
            record["level"] = level
            record["message"] = message
            record["name"] = self.name
            if _format_asctime:
                tm = time.localtime()
                record["asctime"] = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}" \
                    .format(tm[0], tm[1], tm[2], tm[3], tm[4], tm[5])
            if _format_chrono:
                record["chrono"] = "{:f}".format(time.ticks_diff(time.ticks_ms(), self.start_ms) / 1000)

            log_str = _format % record + "\n"

            if _filename is None:
                _ = _stream.write(log_str)
            else:
                with open(_filename, "a") as fp:
                    fp.write(log_str)

        except Exception as e:
            print("--- Logging Error ---")
            print(repr(e))
            print("Message: '" + message + "'")
            print("Arguments:", args)
            print("Format String: '" + _format + "'")
            raise e

    def set_level(self, level):
        self.level = level

    def debug(self, message, *args):
        self.log(DEBUG, message, *args)

    def info(self, message, *args):
        self.log(INFO, message, *args)

    def warning(self, message, *args):
        self.log(WARNING, message, *args)

    def error(self, message, *args):
        self.log(ERROR, message, *args)

    def critical(self, message, *args):
        self.log(CRITICAL, message, *args)

    def exception(self, ex, message, *args):
        self.log(ERROR, message, *args)

        if _filename is None:
            sys.print_exception(ex, _stream)
        else:
            with open(_filename, "a") as fp:
                sys.print_exception(ex, fp)


def get_logger(name="root"):
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]


def basic_config(level=None, filename=None, filemode='a', formatting=None):
    global _filename, _level, _format, _format_chrono, _format_asctime
    _filename = filename
    _level = level
    if formatting is not None:
        _format = formatting
        _format_chrono = "chrono" in _format
        _format_asctime = "asctime" in _format

    if filename is not None and filemode != "a":
        with open(filename, "w"):
            pass  # clear log file


def set_level(level):
    get_logger().set_level(level)


def debug(message, *args):
    get_logger().debug(message, *args)


def info(message, *args):
    get_logger().info(message, *args)


def warning(message, *args):
    get_logger().warning(message, *args)


def error(message, *args):
    get_logger().error(message, *args)


def critical(message, *args):
    get_logger().critical(message, *args)


def exception(ex, message, *args):
    get_logger().exception(ex, message, *args)
