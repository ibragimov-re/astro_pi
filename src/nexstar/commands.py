from enum import Enum


class Command(bytes, Enum):
    HANDSHAKE = b'K'
    VERSION = b'V'
    PASS_THROUGH = b'P'
    GET_MODEL = b'm'
    GET_LOCATION = b'w'
    SET_LOCATION = b'W'
    GET_TIME = b'h'
    SET_TIME = b'H'
    GET_TRACKING_MODE = b't'
    SET_TRACKING_MODE = b'T'
    ALIGN_COMPLETE = b'J'
    SYNC_RA_DEC = b'S'
    SYNC_RA_DEC_PRECISION = b's'
    GOTO_RA_DEC = b'R'
    GOTO_RA_DEC_PRECISION = b'r'
    GOTO_AZM_ALT = b'B'
    GOTO_AZM_ALT_PRECISION = b'b'
    GOTO_IN_PROG = b'L'
    CANCEL_GOTO = b'M'
    GET_RA_DEC = b'E'
    GET_RA_DEC_PRECISION = b'e'
    GET_AZM_ALT = b'Z'
    GET_AZM_ALT_PRECISION = b'z'
    END = b'#'
    ZERO = b'\x00'

    def to_char(self):
        return chr(self[0])

