import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('./log.txt', mode="a")

fm = logging.Formatter('%(asctime)s - %(filename)s[Line:%(lineno)d] - %(levelname)s: %(message)s')
fh.setFormatter(fm)
logger.addHandler(fh)