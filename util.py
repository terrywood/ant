# coding=utf-8
from datetime import datetime
from easytrader.log import log
from datetime import datetime
import time


def is_trade_date():
    day_of_week = datetime.now().weekday()
    if day_of_week < 5:
        h = datetime.now().hour
        if 9 <= h < 15:
            return True
        else:
            return False
    else:
        return False


def is_today(local_date):
    today = datetime.now()
    if local_date.day == today.day and local_date.month == today.month and local_date.year == today.year:
        return True



