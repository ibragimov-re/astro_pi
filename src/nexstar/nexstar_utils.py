import datetime
import os

from utils.location import Coordinate, Location
from src.utils import astropi_utils
from .commands import Command


def to_byte_command(val: int):
    return astropi_utils.int_to_byte(val) + Command.END


def strip_command_letter(data):
    return data.decode('ascii')[1:]


def get_time():
    return get_current_time_bytes()


def byte_to_date_time_utc_string(data: bytes):
    hour = data[1]  # R
    minute = data[2]  # S
    second = data[3]  # T
    month = data[4]  # U
    day = data[5]  # V
    year = data[6]  # W
    tz_offset = data[7]  # X
    is_dst = data[8]  # Q

    return f"{year}-{month}-{day} {hour}:{minute}:{second}"


def byte_to_datetime_utc(data: bytes) -> datetime:
    hour = int(data[1])  # Q
    minute = int(data[2])  # R
    second = int(data[3])  # S
    month = int(data[4])  # T
    day = int(data[5])  # U
    year = int(data[6]) + 2000  # V
    tz_offset = int(data[7])  # W
    is_dst = bool(data[8])  # X 1 to enable Daylight Savings and 0 for Standard Time

    datetime_utc = datetime.datetime(year, month, day, hour, minute, second)
    return datetime_utc


def set_hardware_clock(dt: datetime):
    cmd = f"sudo hwclock --set --date '{dt.isoformat()}' --utc"
    os.system(cmd)
    print(f"Аппаратные часы установлены: {dt}")


def get_current_time_bytes():
    now = astropi_utils.get_current_time()
    is_dst = astropi_utils.is_day_time()
    tz_offset = astropi_utils.get_timezone_offset()

    return time_to_bytes(now.hour, now.minute, now.second, now.month, now.day, now.year, is_dst, tz_offset)


def time_to_bytes(hour, minute, second, month, day, year, is_dst, tz_offset):
    return bytes([
        hour,
        minute,
        second,
        month,
        day,
        year % 100,  # year without age, 0-99
        tz_offset,
        is_dst
    ]) + Command.END


def bytes_to_location(data: bytes):
    # 1st byte is command
    lat_deg = data[1]  # A
    lat_min = data[2]  # B
    lat_sec = data[3]  # C
    north_south = data[4]  # D

    long_deg = data[5]  # E
    long_min = data[6]  # F
    long_sec = data[7]  # G
    east_west = data[8] if len(data) > 8 else 0  # H

    lat_coord = Coordinate(deg=lat_deg, min=lat_min, sec=lat_sec)
    long_coord = Coordinate(deg=long_deg, min=long_min, sec=long_sec)

    loc = Location(
        lat=lat_coord,
        long=long_coord,
        north_south=north_south,
        east_west=east_west
    )
    return loc


def location_to_bytes(location: Location):
    if not location:
        return None

    lat = location.lat
    long = location.long

    return bytes([
        lat.deg,
        lat.min,
        lat.sec,
        location.north_south,
        long.deg,
        long.min,
        long.sec,
        location.east_west
    ])
