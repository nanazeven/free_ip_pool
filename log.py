import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./log.log', mode="a")
fh.setFormatter(logging.Formatter('%(asctime)s - %(filename)s[Line:%(lineno)d] - %(levelname)s: %(message)s'))
logger.addHandler(fh)
