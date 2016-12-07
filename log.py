#!/bin/env python
# coding:utf-8

import logging
logger = logging.getLogger('ant')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('console.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)