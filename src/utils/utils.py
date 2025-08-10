import datetime
import socket
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


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google DNS
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"
