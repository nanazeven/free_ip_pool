import logging,logging.handlers
import datetime

logger = logging.getLogger('pool')
logger.setLevel(logging.INFO)
rh = logging.handlers.RotatingFileHandler('./logs/pool.log', maxBytes=500, backupCount=5,encoding='utf-8')
rh.setFormatter(logging.Formatter('%(asctime)s - %(filename)s[Line:%(lineno)d] - %(levelname)s: %(message)s'))



logger.addHandler(rh)
