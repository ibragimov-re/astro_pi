#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import math
import socket
import time

from astropy.coordinates import Longitude
from astropy.time import Time
from astropy.utils import iers
iers.conf.auto_download = False
iers.conf.auto_max_age = None

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

def calculate_local_sidereal_time_old(longitude_deg, obs_time: datetime.datetime=datetime.datetime.now(datetime.UTC)):
    """
    Вычисляет местное звездное время в градусах

    Args:
        obs_time: время наблюдения
        longitude_deg: долгота наблюдателя в градусах
    """
    # JD2000 = 2451545.0
    j2000 = datetime.datetime(2000, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)  # J2000 эпоха

    # Разница в днях от J2000
    days_since_j2000 = (obs_time - j2000).total_seconds()  / 60 / 60 / 24

    # Звездное время в Гринвиче (в градусах)
    # 280.46061837° - начальное смещение
    # 360.98564736629° - скорость вращения Земли в градусах/день
    gmst_deg = (280.46061837 + 360.98564736629 * days_since_j2000) % 360

    gmst_time = deg_to_time(gmst_deg)

    print(f'Расчетное GMST: {gmst_deg}°, {gmst_time.strftime("%H:%M:%S")}')

    # Местное звездное время = GMST + долгота
    lst_deg = (gmst_deg + longitude_deg) % 360

    # Преобразование в формат часов, минут, секунд
    lst_time = deg_to_time(lst_deg)

    print(f'Расчетное LST: {lst_deg}°, {lst_time.strftime("%H:%M:%S")}')

    return lst_deg

def calculate_local_sidereal_time(longitude_deg: float, obs_time: datetime.datetime = None) -> float:
    if obs_time is None:
        obs_time = datetime.datetime.now(datetime.timezone.utc)
    else:
        obs_time = obs_time.astimezone(datetime.timezone.utc)
    t = Time(obs_time, scale="utc")

    lst_deg: Longitude = t.sidereal_time('mean', longitude=longitude_deg)
    # lst_time = lst_deg.to_string(unit='hour')
    #
    # print(f'Расчетное LST: {lst_deg.deg}°, {lst_time}')
    return lst_deg.deg

def calculate_local_sidereal_time2(
    longitude_deg: float,
    obs_time: datetime.datetime = None
) -> float:
    """
    Вычисляет местное звёздное время (LST) в градусах.
    """

    if obs_time is None:
        obs_time = datetime.datetime.now(datetime.timezone.utc)
    else:
        obs_time = obs_time.astimezone(datetime.timezone.utc)

    gmst_deg = gmst_from_datetime(obs_time)
    lst_deg = (gmst_deg + longitude_deg) % 360

    gmst_time = deg_to_time(gmst_deg)
    lst_time = deg_to_time(lst_deg)

    print(f'Расчетное GMST: {gmst_deg}°, {gmst_time.strftime("%H:%M:%S")}')
    print(f'Расчетное LST: {lst_deg}°, {lst_time.strftime("%H:%M:%S")}')

    return lst_deg


def gmst_from_datetime(obs_time: datetime.datetime) -> float:
    """
    Вычисляет GMST (Гринвичское звёздное время) в градусах
    по стандарту IAU 2006.

    Все коэффициенты разложены и соответствуют официальным
    астрономическим алгоритмам.
    """

    # Юлианская дата и столетия от J2000
    JD = julian_date(obs_time)
    T = (JD - 2451545.0) / 36525

    # ------ Разложенные коэффициенты IAU 2006 ------
    # GMST_0 (звёздное время в 0h UT)
    GMST0_deg = (
        100.46061837
        + 36000.770053608 * T
        + 0.000387933 * T**2
        - (T**3) / 38710000
    )

    # UT в часах
    UT = (
        obs_time.hour
        + obs_time.minute / 60
        + obs_time.second / 3600
        + obs_time.microsecond / 3_600_000_000
    )

    # Ускорение вращения Земли: звёздные сутки ≠ солнечные
    SIDEREAL_RATE = 1.00273790935  # отношение звёздных суток к солнечным

    GMST_deg = (GMST0_deg + SIDEREAL_RATE * UT * 15) % 360

    return GMST_deg


def julian_date(dt: datetime.datetime) -> float:
    """
    Вычисляет Юлианскую дату (JD) из datetime в UTC.
    """
    year = dt.year
    month = dt.month
    day = dt.day + (dt.hour + (dt.minute + dt.second / 60) / 60) / 24

    if month <= 2:
        year -= 1
        month += 12

    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)

    JD = (
        math.floor(365.25 * (year + 4716))
        + math.floor(30.6001 * (month + 1))
        + day
        + B
        - 1524.5
    )

    return JD

def deg_to_time(deg: float) -> datetime.time:
    """Преобразование в формат часов, минут, секунд"""
    hours_float = deg / 15.0
    hours = int(hours_float)
    minutes = int((hours_float - hours) * 60)
    seconds = int(((hours_float - hours) * 60 - minutes) * 60)
    return datetime.time(hours, minutes, seconds, 0, tzinfo=datetime.timezone.utc)