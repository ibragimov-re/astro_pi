from src.location import Coordinate, Location
from src.utils import utils
from src.utils import coords
from src.server import Server
from src.nexstar.commands import Command, Device, Model


# manual by commands https://s3.amazonaws.com/celestron-site-support-files/support_files/1154108406_nexstarcommprot.pdf


class ServerNexStar(Server):
    buffer = 8
    major = 1
    minor = 0
    model = Model.ADVANCED_GT
    has_gps = False

    def __init__(self, host='0.0.0.0', port=4030):
        super().__init__(host, port, Server.name + ' [NexStar]')

    def get_buffer(self):
        return self.buffer

    def handshake(self, data):
        self.logger.info(f"Клиент запрашивает состояние. ОК")
        return data[1:] + Command.END

    def handle_command(self, data):

        if not isinstance(data, bytes):
            return None

        self.logger.debug(f"Получена команда: {data}")

        if not data:
            return None

        if data == Command.END:
            return b''
        elif data.startswith(Command.PASS_THROUGH):
            return self.pass_through(data)
        elif data.startswith(Command.GET_LOCATION):
            return self.get_location()
        elif data.startswith(Command.SET_LOCATION):
            return self.set_location(data)
        elif data.startswith(Command.GET_RA_DEC_PREC):
            return self.get_ra_dec_precise()
        elif data.startswith(Command.SYNC_RA_DEC):
            return self.sync_ra_dec(data)
        elif data.startswith(Command.SYNC_RA_DEC_PREC):
            return self.sync_ra_dec_precise(data)
        elif data.startswith(Command.GET_TIME):
            return get_time()
        elif data.startswith(Command.HANDSHAKE):
            return self.handshake(data)
        elif data.startswith(Command.VERSION):
            return self.get_version()
        elif data.startswith(Command.GOTO_IN_PROG):
            return self.is_goto_in_progress()
        elif data.startswith(Command.ALIGN_COMPLETE):
            return self.is_alignment_in_prog()
        elif data.startswith(Command.GET_TRACKING_MODE):
            return self.get_tracking_mode()
        elif (data.startswith(Command.MODEL)):
            return self.get_model()

        return Command.END

    def get_version(self):
        self.logger.info(f"Запрос версии, текущая версия: {self.major}.{self.minor}")

        return bytes([self.major, self.minor]) + Command.END

    def get_device_version(self, cmd):
        dev_code = cmd[2]  # Код устройства

        try:
            device = Device(dev_code)  # Преобразуем в Enum
        except ValueError:
            device = f"Unknown device ({dev_code})"

        self.logger.info(f"Получена информация об устройстве. Device: {device.name}")

        return self.get_version()

    def get_model(self):
        self.logger.info(f"Запрос модели. Текущая модель: {self.model}")
        return self.model.value.to_bytes(1, 'little') + Command.END

    def get_tracking_mode(self):
        return self.tracking_mode.to_bytes(1, 'little') + Command.END

    def pass_through(self, data):
        byte_3 = data[2]

        if byte_3 == Device.AZM_RA_MOTOR:
            return self.get_version()
        elif byte_3 == Device.ALT_DEC_MOTOR:
            return self.get_version()
        elif byte_3 == Device.GPS:  # это GPS команды
            return self.gps_commands(data)
        else:
            # Неизвестная команда
            return Command.END

    def gps_commands(self, data):
        byte_4 = data[3]
        if byte_4 == 55:  # Is GPS Linked? (X > 0 if linked, 0 if not linked)
            return bytes([0]) + Command.END if not self.has_gps else bytes([1]) + Command.END
        elif byte_4 == 254:  # Get Device Version
            return self.get_version()  # not sure that's right
        else:
            # Неизвестная команда
            return Command.END

    def get_location(self):
        return self.coord_bytes()

    def set_location(self, data: bytes):
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

        self.location = Location(
            lat=lat_coord,
            long=long_coord,
            north_south=north_south,
            east_west=east_west
        )

    def is_goto_in_progress(self):
        return bytes([self.goto_in_progress]) + Command.END

    def is_alignment_in_prog(self):
        return bytes([self.alignment_completed]) + Command.END

    # Собираем байтовую строку кокординат
    def coord_bytes(self):
        if not self.location:
            return Command.END

        lat = self.location.lat
        long = self.location.long

        coord_arr = [
            lat.deg,
            lat.min,
            lat.sec,
            self.location.north_south,
            long.deg,
            long.min,
            long.sec
            #self.location.east_west
        ]

        return bytes(coord_arr) + Command.END

    def get_ra_dec_precise(self):
        ra = coords.hex_to_degrees("34AB0500", True)
        dec = coords.hex_to_degrees("12CE0500", True)

        raP = 38.012
        decP = 89.259

        raPhex = coords.degrees_to_hex(raP, True)
        decPhex = coords.degrees_to_hex(decP, True)

        return b"1B09A050,3F7D6305#"
        #return b"34AB0500,12CE0500#"  # TODO: временное решение

    def sync_ra_dec(self, data):
        return Command.END

    def sync_ra_dec_precise(self, data):
        ra = data.decode('ascii').lstrip('s')
        self.last_ra = coords.hex_to_degrees(ra, True)
        # why `DEC` is not receive? Only `RA`
        return Command.END


def get_time():
    return get_current_time_bytes()


def get_current_time_bytes():
    now = utils.get_current_time()
    tz_offset = utils.get_timezone_offset()
    is_dst = utils.is_day_time()

    return bytes([
        now.hour,
        now.minute,
        now.second,
        now.month,
        now.day,
        now.year % 100,  # год без века, 0-99
        tz_offset,
        is_dst
    ]) + Command.END
