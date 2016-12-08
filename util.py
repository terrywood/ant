# coding=utf-8
from datetime import datetime

holiday = ["20170102", "20170103", "20170127", "20170130", "20170131", "20170201", "20170202", "20170403", "20170404",
           "20170405"]


def is_trade_date():
    today = datetime.now()
    if today.strftime('%Y%m%d') in holiday:
        return False
    day_of_week = today.weekday()
    if day_of_week < 5:
        h = today.hour
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
