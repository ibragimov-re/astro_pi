from enum import IntEnum


class Device(IntEnum):
    AZM_RA_MOTOR = 16
    ALT_DEC_MOTOR = 17
    GPS = 176
    RTC = 178  # Real-Time Clock

class Direction(IntEnum):
    POSITIVE = 36
    NEGATIVE = 37

class Extra(IntEnum):
    GET_DEVICE_VERSION = 254
    IS_GPS_LINKED = 55

class Model(IntEnum):
    GPS_SERIES = 1
    I_SERIES = 3
    I_SERIES_SE = 4
    CGE = 5
    ADVANCED_GT = 6
    SLT = 7
    CPC = 9
    GT = 10
    SE_4_5 = 11
    SE_6_8 = 12