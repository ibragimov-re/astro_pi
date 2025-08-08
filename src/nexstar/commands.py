from enum import IntEnum, Enum


class Command(bytes, Enum):
    HANDSHAKE = b'K'
    VERSION = b'V'
    PASS_THROUGH = b'P'
    MODEL = b'm'
    GET_LOCATION = b'w'
    SET_LOCATION = b'W'
    GET_RA_DEC = b'E'
    GET_RA_DEC_PREC = b'e'
    GET_AZM_ALT = b'Z'
    GET_AZM_ALT_PREC = b'z'
    GET_TIME = b'h'
    GET_TRACKING_MODE = b't'
    GOTO_IN_PROG = b'L'
    ALIGN_COMPLETE = b'J'
    END = b'#'
    ZERO = b'0'


class Device(IntEnum):
    AZM_RA_MOTOR = 16
    ALT_DEC_MOTOR = 17
    GPS = 176
    RTC = 178


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
