import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)

def log(msg, level='info'):
    lookup = {
        'info': logging.info,
        'error': logging.error,
        'warning': logging.warning}
    lookup[level](msg)