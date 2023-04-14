#!/usr/bin/env python
import logging
from functools import partial, partialmethod
import time
logging.TRACE = logging.DEBUG - 5
logging.addLevelName(logging.TRACE, 'TRACE')
logging.Logger.trace = partialmethod(logging.Logger.log, logging.TRACE)
logging.trace = partial(logging.log, logging.TRACE)


def set_log_level(log_level):
    logging.getLogger().setLevel(log_level.value)
    logging.info(f'Log level set to {log_level.value}')


logging.Formatter.converter = time.gmtime
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format('.', 'frog'))
logFormatter = logging.Formatter(
    '[%(asctime)sUTC] - [%(levelname)s] - [%(threadName)-12.12s] - [%(filename)s[%(lineno)d].%(funcName)s]: %(message)s')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

logFormatter = logging.Formatter(
    "[%(asctime)sUTC] - [%(levelname)s]  %(message)s")
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
