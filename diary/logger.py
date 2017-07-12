import logging


default_formatter = logging.Formatter(
    '%(asctime)s %(filename)s:%(lineno)d %(name)-12s '
    '%(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S'
)

def get_stream_handler(level=None, formatter=None):
    if not level:
        level = logging.INFO
    if not formatter:
        formatter = default_formatter

    handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def configure(logger, level, formatter=None):
    s_handler = get_stream_handler(level=level, formatter=formatter)

    logger.addHandler(s_handler)
    logger.setLevel(level)
