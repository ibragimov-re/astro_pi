import datetime
import logging

from .nexstar_utils import strip_command_letter, to_byte_command, get_time, bytes_to_location, \
    location_to_bytes, byte_to_datetime_utc
from src.nexstar.commands import Command, Device, Model
from src.server import Server
from src.utils import astropi_utils
from src.utils.tracking_mode import TrackingMode


# manual by commands https://s3.amazonaws.com/celestron-site-support-files/support_files/1154108406_nexstarcommprot.pdf


class Mouth:
    def __init__(self, model, has_gps, tracking_mode, name="No name NexStar mount with GoTo"):
        self.name = name
        self.model = model
        self.has_gps = has_gps
        self.tracking_mode = tracking_mode  # как я понял это определяет какой будет тип компенсации вращения - по экваториальной или азимутальной оси


CGX_MOUTH = Mouth(Model.CGE, True, TrackingMode.EQ_NORTH, "Celestron Montatura CGX GoTo")
SE_MOUTH = Mouth(Model.SE_4_5, True, TrackingMode.ALT_AZ, "Celestron SE 5")
DEFAULT = SE_MOUTH

POLAR_RA_DEC = [38.044259548187256, 89.259]  # Polar Star RA/DEC
ZERO_RA_DEC = [0.0, 0.0]
DEFAULT_TARGET = POLAR_RA_DEC

APP_VERSION = [4, 10]
DEVICE_VERSION = [1, 0]

BUFFER = 18  # in documentation, the longest command is 18 bytes


class ServerNexStar(Server):
    buffer = 18
    major = APP_VERSION[0]
    minor = APP_VERSION[1]
    last_ra = DEFAULT_TARGET[0]
    last_dec = DEFAULT_TARGET[1]

    def __init__(self, host='0.0.0.0', port=4030):
        super().__init__(host, port, Server.name + ' [NexStar]')
        self.mouth = DEFAULT
        self.last_ra = DEFAULT_TARGET[0]
        self.last_dec = DEFAULT_TARGET[1]

    def get_buffer(self):
        return self.buffer

    def handshake(self, data):
        self.logger.info(f"Клиент запрашивает состояние. ОК")
        return data[1:] + Command.END

    def set_time(self, data):
        now = datetime.datetime.now()
        dt = byte_to_datetime_utc(data)
        # TODO: set system time
        # set_hardware_clock(dt)
        diff = (now - dt).total_seconds()
        if abs(diff) < 10.0:
            self.logger.info(f"Рассинхронизация времени не существенная: {diff:+.2f} секунд(ы)")
            return Command.END
        else:
            return b''

    def handle_command(self, data):

        if not isinstance(data, bytes):
            return None

        self.logger.debug(f"Получена команда: {data}")

        if not data:
            return None

        if data == Command.END:
            return b''
        elif data == Command.ZERO:
            return data  # not sure that's right
        elif data.startswith(Command.PASS_THROUGH):
            return self.pass_through(data)
        elif data.startswith(Command.GET_LOCATION):
            return self.get_location()
        elif data.startswith(Command.SET_LOCATION):
            return self.set_location(data)
        elif data.startswith(Command.GET_RA_DEC):
            return self.get_ra_dec(False)
        elif data.startswith(Command.GET_RA_DEC_PRECISION):
            return self.get_ra_dec(True)
        elif data.startswith(Command.SYNC_RA_DEC):
            return self.sync_ra_dec(data, False)
        elif data.startswith(Command.SYNC_RA_DEC_PRECISION):
            return self.sync_ra_dec(data, True)
        elif data.startswith(Command.GET_TIME):
            return get_time()
        elif data.startswith(Command.SET_TIME):
            return self.set_time(data)
        elif data.startswith(Command.HANDSHAKE):
            return self.handshake(data)
        elif data.startswith(Command.VERSION):
            return self.get_app_version()
        elif data.startswith(Command.GOTO_IN_PROG):
            return self.is_goto_in_progress()
        elif data.startswith(Command.ALIGN_COMPLETE):
            return self.is_alignment_in_prog()
        elif data.startswith(Command.GET_TRACKING_MODE):
            return self.get_tracking_mode()
        elif data.startswith(Command.GOTO_RA_DEC):
            return self.goto_ra_dec(data)
        elif data.startswith(Command.GOTO_RA_DEC_PRECISION):
            return self.goto_ra_dec_prec(data)
        elif data.startswith(Command.MODEL):
            return self.get_model()
        elif data.startswith(Command.CANCEL_GOTO):
            return self.cancel_goto()
        else:
            return Command.END

    def get_app_version(self):
        self.logger.info(f"Версия приложения: v{self.major}.{self.minor}")

        return self.version_to_byte(APP_VERSION[0], APP_VERSION[1])

    @staticmethod
    def version_to_byte(major, minor):
        return bytes([major, minor]) + Command.END

    def get_device_info(self, dev_code):

        try:
            device = Device(dev_code)
        except ValueError:
            device = f"Неизвестное устройство код: {dev_code}"

        self.logger.info(f"Получена информация об устройстве. Device: {device.name}")

        return self.get_device_version()

    def get_device_version(self):
        self.logger.info(f"Версия устройства: v{DEVICE_VERSION[0]}.{DEVICE_VERSION[1]}")

        return self.version_to_byte(DEVICE_VERSION[0], DEVICE_VERSION[1])

    def get_model(self):
        self.logger.info(f"Текущая модель: {self.mouth.model.name}")
        return to_byte_command(self.mouth.model.value)

    def get_tracking_mode(self):
        return to_byte_command(self.mouth.tracking_mode.value)

    def has_gps(self):
        return self.mouth.has_gps

    def pass_through(self, data):
        dev_code = data[2]

        if dev_code == Device.GPS:
            return self.gps_commands(data)  # get GPS commands
        else:
            return self.get_device_info(dev_code)

    def gps_commands(self, data):
        byte_4 = data[3]
        if byte_4 == 55:  # Is GPS Linked? (X > 0 if linked, 0 if not linked)
            return bytes([0]) + Command.END if not self.has_gps() else bytes([1]) + Command.END
        elif byte_4 == 254:  # Get Device Version
            self.logger.info(f"Версия GPS: v{1}.{3}")
            return self.version_to_byte(1, 3)
        else:  # Неизвестная команда
            return Command.END

    def get_location(self):
        self.logger.info(f"Текущии GPS координаты: {self.location}")
        return self.coord_bytes()

    def set_location(self, data: bytes):
        self.location = bytes_to_location(data)
        self.logger.info(f"GPS координаты заданы: {self.location}")

    def is_goto_in_progress(self):
        return bytes([self.goto_in_progress]) + Command.END

    def is_alignment_in_prog(self):
        return bytes([self.alignment_completed]) + Command.END

    # Собираем байтовую строку кокординат
    def coord_bytes(self):
        if not self.location:
            return Command.END

        return location_to_bytes(self.location) + Command.END

    def get_ra_dec(self, precise: bool = True):
        last_ra_hex = self.get_last_ra_hex(precise)
        last_dec_hex = self.get_last_dec_hex(precise)

        self.logger.info(f"Текущие координаты наведения: П.В (Ra):{self.last_ra} ({last_ra_hex}), Скл (Dec):{self.last_dec} ({last_dec_hex})")

        return last_ra_hex.encode('ascii') + b',' + last_dec_hex.encode('ascii') + Command.END

    def get_last_dec_hex(self, precise: bool = True):
        return astropi_utils.degrees_to_hex(self.last_dec, precise)

    def get_last_ra_hex(self, precise: bool = True):
        return astropi_utils.degrees_to_hex(self.last_ra, precise)

    def sync_ra_dec_precise(self, data):
        return self.sync_ra_dec(data, True)

    def sync_ra_dec(self, data, precise: bool = False):
        self.goto_in_progress = True
        ra_dec = strip_command_letter(data)
        ra_dec_arr = ra_dec.split(',')
        ra_hex = ra_dec_arr[0]
        dec_hex = ra_dec_arr[1]

        self.last_ra = astropi_utils.hex_to_degrees(ra_hex, precise)
        self.last_dec = astropi_utils.hex_to_degrees(dec_hex, precise)

        self.logger.info(f"Синхронизация по координатам: П.В (Ra):{self.last_ra} ({ra_hex}), Скл (Dec): {self.last_dec} ({dec_hex})")

        self.goto_in_progress = False

        return Command.END

    def goto_ra_dec_prec(self, data):
        return self.goto_ra_dec(data, True)

    def goto_ra_dec(self, data, precise: bool = False):
        self.goto_in_progress = True
        ra_dec = strip_command_letter(data)
        ra_dec_arr = ra_dec.split(',')

        ra_hex = ra_dec_arr[0]
        dec_hex = ra_dec_arr[1]

        self.last_ra = astropi_utils.hex_to_degrees(ra_hex, precise)
        self.last_dec = astropi_utils.hex_to_degrees(dec_hex, precise)

        self.logger.info(f"Наведение по координатам: П.В (Ra):{self.last_ra}, Скл (Dec): {self.last_dec}")

        self.goto_in_progress = False

        return Command.END
