import logging

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)


def get_logger(*args, **kwargs):
    logger = logging.getLogger(*args, **kwargs)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
