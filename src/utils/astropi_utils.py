#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import math
import socket
import time
from astropy.time import Time
import astropy.units as u

from utils.location import Coordinate

STANDARD = 0x10000      # 16-bit: 65536
PRECISE_NS = 0x1000000  # 24-bit: 16777216, this precision in NexStar documentation
PRECISE = 0x100000000   # 32-bit: 4294967296, now Stellarium uses this precision

MASK_16_BIT = 0xFFFF        # 16-bit mask
MASK_24_BIT = 0xFFFFFF      # 24-bit mask
MASK_32_BIT = 0xFFFFFFFF    # 32-bit mask

_SCALE_CACHE = {
    False: STANDARD,
    True: PRECISE
}

_SCALE_DEG_TO_HEX_CACHE = {
    False: STANDARD / 360.0,
    True: PRECISE / 360.0
}

_SCALE_HEX_TO_DEG_CACHE = {
    False: 360.0 / STANDARD,
    True: 360.0 / PRECISE
}

_DIGIT_CACHE = {
    False: 4,
    True: 8
}


def get_current_time():
    return datetime.datetime.now()

def get_current_time_utc():
    return datetime.datetime.now(datetime.UTC)


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


def int_to_byte(val: int):
    return val.to_bytes(1, 'little')


def hex_to_degrees(hex_degrees: str, precise: bool) -> float:
    """
    Переводит шестнадцатиричный формат координат (0000, FFFF) в десятичне градусы (0, 360]

    Параметры:
        hex_degrees (float): Исходный угол в шестнадцатеричном формате (может 4-х или 8 разрядным).
        precise (bool): Точный формат или стандартный

    Возвращает:
        float: десятичне градусы, точность зависит от параметра точности (precise),
               для стандартного это 19.8 арксекунды, а для точного 0.08 арксекунды.

    Примеры:
        >>> hex_to_degrees("12CE", False)
        26.4441
        >>> hex_to_degrees("1B0D70A6", True)
        38.04257831
    """
    value = int(hex_degrees, 16)

    # используем заранее просчитанный коофициент: degrees * 360 / PRECISISON, это эквивалентно: degrees / PRECISISON * 360
    degrees = value * _SCALE_HEX_TO_DEG_CACHE[precise]
    degrees = normalize_angle(degrees)

    return round(degrees, _DIGIT_CACHE[precise])


def degrees_to_hex(degrees: float, precise: bool) -> str:
    """
    Переводит десятичне градусы [0, 360) в шестнадцатиричный формат

    Параметры:
        degrees (float): Исходный угол в градусах (может быть отрицательным).
        precise (bool): Точный формат или стандартный

    Возвращает:
        string: Шестнадцатиричное представление (4 или 8 разрядов в зависимости от параметра точности (precise).

    Примеры:
        >>> degrees_to_hex(26.4441, False)
        "12CE"
        >>> degrees_to_hex(-38.04256439, True)
        1B0D70A6
    """
    degrees = normalize_angle(degrees)

    # используем заранее просчитанный коофициент: degrees * RECISISON / 360, это эквивалентно: degrees / 360 * PRECISISON
    int_value = round(degrees * _SCALE_DEG_TO_HEX_CACHE[precise])

    return int_to_hex(int_value, _DIGIT_CACHE[precise])


def normalize_angle(angle: float):
    return angle % 360.0

def normalize_radians(angle: float):
    return angle % (2 * math.pi)

def normalize_degrees_signed(angle):
    while angle < -180.0:
        angle += 360.0
    while angle >= 180.0:
        angle -= 360.0
    return angle

def normalize_degrees_unsigned(angle):
    while angle < 0.0:
        angle += 360.0
    while angle >= 360.0:
        angle -= 360.0
    return angle

def int_to_hex(value: int, digit: int) -> str:
    """Переводит целое число в шестнадцатеричную строку с заданным количеством разрядов (digit)"""
    return f"{value:0{digit}X}"


def calculate_lst(utc_time: datetime.datetime, longitude: Coordinate) -> float:
    utc_deg = (utc_time.hour + utc_time.minute / 60 + utc_time.second / 60)
    long_deg_time = longitude.deg / 15 + longitude.min / 60 + longitude.sec / 60
    lst = utc_deg + long_deg_time
    return lst

def calculate_lst_astropy(utc_time: datetime.datetime, longitude_deg: float):
    """
        utc_time: datetime.datetime с tz=timezone.utc
        longitude_deg: восточная долгота в градусах (положительная)
        Возвращает LST в градусах.
        """
    t = Time(utc_time, scale='utc')
    lst = t.sidereal_time('apparent', longitude=longitude_deg * u.deg_C)
    return lst.deg