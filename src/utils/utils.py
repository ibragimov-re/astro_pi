import datetime
import time


def get_current_time():
    return datetime.datetime.now()


def get_timezone_offset():
    tz_offset = -time.timezone // 3600
    if tz_offset < 0:
        tz_offset = 256 + tz_offset

    return tz_offset


# Определяем летнее время
def is_day_time():
    return 1 if time.localtime().tm_isdst > 0 else 0
