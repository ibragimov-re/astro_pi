import datetime
from os.path import altsep

from src.nexstar.commands import Command
from src.server import Server
from src.utils import astropi_utils
from utils import coordinate_utils
from utils.location import SkyCoordinate
from .constants import Device, Direction, Extra
from .nexstar_utils import strip_command_letter, to_byte_command, get_time, bytes_to_location, \
    location_to_bytes, byte_to_datetime_utc

# manual by commands https://s3.amazonaws.com/celestron-site-support-files/support_files/1154108406_nexstarcommprot.pdf

APP_VERSION = [4, 10]
DEVICE_VERSION = [4, 10]
GPS_VERSION = [1, 3]

NEXSTAR_BUFFER = 18  # in documentation, the longest command is 18 bytes


class ServerNexStar(Server):

    def __init__(self, host='0.0.0.0', port=4030, mouth_type='real', sync=False):
        super().__init__(host, port, Server.name, mouth_type, "NexStar", sync)

        self.buffer = NEXSTAR_BUFFER
        self.major = APP_VERSION[0]
        self.minor = APP_VERSION[1]

    def get_buffer(self):
        return self.buffer

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
        elif data.startswith(Command.SET_TRACKING_MODE):
            return self.set_tracking_mode(data)
        elif data.startswith(Command.GOTO_RA_DEC):
            return self.goto_ra_dec(data)
        elif data.startswith(Command.GOTO_RA_DEC_PRECISION):
            return self.goto_ra_dec_prec(data)
        elif data.startswith(Command.GOTO_AZM_ALT):
            return self.goto_az_alt(data)
        elif data.startswith(Command.GOTO_AZM_ALT_PRECISION):
            return self.goto_az_alt_prec(data)
        elif data.startswith(Command.GET_MODEL):
            return self.get_model()
        elif data.startswith(Command.CANCEL_GOTO):
            self.cancel_goto()
            return Command.END
        else:
            return Command.END

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
            self.logger.info(f"Время синхронизировано (рассинхронизация: {diff:+.2f} секунд(ы)")
            return Command.END
        else:
            self.logger.info(f"Время НЕ синхронизировано!")
            return b''

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
        self.logger.info(f"Текущая модель: {self.mouth.params.model.name}")
        return to_byte_command(self.mouth.params.model.value)

    def get_tracking_mode(self):
        self.logger.info(f"Режим отслеживания движения: {self.mouth.params.tracking_mode.name}")
        return to_byte_command(self.mouth.params.tracking_mode.value)

    def set_tracking_mode(self, data):
        self.mouth.params.tracking_mode = data[1:]
        self.logger.info(f"Режим отслеживания движения установлен: {self.mouth.params.tracking_mode}")
        return Command.END

    def has_gps(self):
        return self.mouth.params.has_gps

    def pass_through(self, data):
        dev_code = data[2]
        if dev_code == Device.GPS:
            return self.gps_commands(data)  # get GPS commands
        elif dev_code == Device.AZM_RA_MOTOR:
            direction = data[3]
            speed = data[4]
            slew_angle = 5
            if direction == Direction.POSITIVE:  # '$' → positive → вправо (восток)
                self.logger.info(f"Фиксированный сдвиг по ч.с. по горизонтали со скоростью {speed}")
                self.mouth.slew_motor_h(slew_angle, speed)
            elif direction == Direction.NEGATIVE:  # '%' → negative → влево (запад)
                self.logger.info(f"Фиксированный сдвиг п.ч.с по горизонтали со скоростью {speed}")
                self.mouth.slew_motor_h(-slew_angle, speed)
            elif direction == Extra.GET_DEVICE_VERSION:
                self.logger.info(f"Версия Azm/RA двигателя: v{DEVICE_VERSION[0]}.{DEVICE_VERSION[1]}")
                return self.version_to_byte(DEVICE_VERSION[0], DEVICE_VERSION[1])
            else:
                self.logger.info(f"Необработанный сдвиг {direction}")
            return Command.END
        elif dev_code == Device.ALT_DEC_MOTOR:
            direction = data[3]
            speed = data[4]
            slew_angle = 1
            if direction == Direction.POSITIVE:  # '$' → positive → вверх (север)
                self.logger.info(f"Фиксированный сдвиг по ч.с. по вертикали со скоростью {speed}")
                self.mouth.slew_motor_v(slew_angle, speed)
            elif direction == Direction.NEGATIVE:  # '%' → negative → вниз (юг)
                self.logger.info(f"Фиксированный сдвиг п.ч.с по вертикали со скоростью {speed}")
                self.mouth.slew_motor_v(-slew_angle, speed)
            elif direction == Extra.GET_DEVICE_VERSION:
                self.logger.info(f"Версия Alt/DEC двигателя: v{DEVICE_VERSION[0]}.{DEVICE_VERSION[1]}")
                return self.version_to_byte(DEVICE_VERSION[0], DEVICE_VERSION[1])
            else:
                self.logger.info(f"Необработанный сдвиг {direction}")
            return Command.END
        elif dev_code == Device.RTC:
            return self.rtc_commands(data) # незнаю что возвращать
        else:
            self.logger.warning(f'Неизвестное устройство с кодом: {dev_code}')
            return Command.END

    def rtc_commands(self, data):
        return Command.END

    def gps_commands(self, data):
        byte_4 = data[3]
        if byte_4 == Extra.IS_GPS_LINKED:  # Is GPS Linked? (X > 0 if linked, 0 if not linked)
            return bytes([0]) + Command.END if not self.mouth.params.has_gps else bytes([1]) + Command.END
        elif byte_4 == Extra.GET_DEVICE_VERSION:  # Get Device Version
            if self.mouth.params.has_gps:
                self.logger.info(f"GPS активен, версия: v{GPS_VERSION[0]}.{GPS_VERSION[1]}")
                return self.version_to_byte(GPS_VERSION[0], GPS_VERSION[1])
            else:
                self.logger.info(f"GPS не активен")
                return bytes([0]) + Command.END
        else:  # Неизвестная команда
            return Command.END

    def get_location(self):
        if self.location:
            self.logger.info(f"Текущии GPS координаты: {self.location}")
        else:
            self.logger.info(f"Текущии GPS координаты не заданы")

        return self.coord_bytes() + Command.END

    def set_location(self, data: bytes):
        self.location = bytes_to_location(data)
        self.logger.info(f"GPS координаты заданы: {self.location}")

    def is_goto_in_progress(self):
        if self.mouth.goto_in_progress:
             self.logger.info(f"Монтировка в процессе наведения GOTO (Ra: {self.get_sync().ra_az_h}, Dec: {self.get_sync().dec_alt_v})")

        return bytes([self.mouth.goto_in_progress]) + Command.END

    def is_alignment_in_prog(self):
        # if self.alignment_completed:
        #     self.logger.info(f"Монтировка выравнена")
        # else:
        #     self.logger.info(f"Монтировка НЕ выравнена")
        return bytes([self.alignment_completed]) + Command.END

    # Собираем байтовую строку кокординат
    def coord_bytes(self):
        if not self.location:
            return Command.END

        # return location_to_bytes(self.location) + Command.END
        return location_to_bytes(self.location)

    def get_ra_dec(self, precise: bool = True):
        """
                Местоположение возвращается в виде шестнадцатеричного значения, представляющего долю оборота вокруг оси.
            Ниже приведены два примера:
            Если команда Get RA/DEC возвращает значение 34AB,12CE, то значение DEC равно 12CE в шестнадцатеричном формате. В процентах
            от оборота это равно 4814/65536 = 0,07346. Чтобы рассчитать градусы, просто умножьте на 360, что даст значение
            26,4441 градуса.
        """
        ra = self.get_current().get_ra()
        dec = self.get_current().get_dec()

        ra_hex = astropi_utils.degrees_to_hex(ra, precise)
        dec_hex = astropi_utils.degrees_to_hex(dec, precise)

        # self.logger.info(f"Текущая цель (RA/Dec): {ra:.4f}° / {dec:.4f}°")

        return ra_hex.encode('ascii') + b',' + dec_hex.encode('ascii') + Command.END

    def sync_ra_dec_precise(self, data):
        return self.sync_ra_dec(data, True)

    def sync_ra_dec(self, data, precise: bool = False):
        self.logger.info(f"Старт команды SYNC (точный режим: {precise})")
        self.mouth.goto_in_progress = True
        ra_dec = strip_command_letter(data)
        ra_dec_arr = ra_dec.split(',')
        ra_hex = ra_dec_arr[0]
        dec_hex = ra_dec_arr[1]

        prec_ra = astropi_utils.hex_to_degrees(ra_hex, precise)
        prec_dec = astropi_utils.hex_to_degrees(dec_hex, precise)

        self.mouth.set_sync(SkyCoordinate(prec_ra, prec_dec))

        self.logger.info(
            f"Синхронизация по координатам: П.В (Ra):{self.get_sync().get_ra():.2f} ({ra_hex}), Скл (Dec): {self.get_sync().get_dec():.2f} ({dec_hex})")

        self.mouth.goto_in_progress = False

        return Command.END

    def goto_ra_dec_prec(self, data):
        return self.goto_ra_dec(data, True)

    def goto_ra_dec(self, data, precise: bool = False):
        self.logger.info(f"Старт команды GOTO Ra/Dec (точный режим: {precise})")
        self.mouth.goto_in_progress = True

        ra_dec = strip_command_letter(data)
        ra_dec_arr = ra_dec.split(',')

        # Координаты в J2000 для лога
        ra_target_deg = astropi_utils.hex_to_degrees(ra_dec_arr[0], precise)
        dec_target_deg = astropi_utils.hex_to_degrees(ra_dec_arr[1], precise)

        # Преобразование в углы моторов
        target_motor_ra = ra_target_deg  # [0, 360)
        target_motor_dec = dec_target_deg  # [-90, 90]

        # Текущие углы моторов
        current_motor_ra = self.mouth.current.get_ra()
        current_motor_dec = self.mouth.current.get_dec()

        # Считаем разницу (относительные углы для поворота)
        # Учитываем кратчайший путь для RA (через 0°/360°)
        delta_ra = astropi_utils.normalize_degrees_signed(current_motor_ra - target_motor_ra)
        delta_dec = astropi_utils.normalize_degrees_signed(target_motor_dec - current_motor_dec)

        self.logger.info(f"Текущая цель (RA/Dec): {self.get_current().get_ra():.4f}° / {self.get_current().get_dec():.4f}°")
        self.logger.info(f"Текущая цель (J2000 RA/Dec): {coordinate_utils.toJ2000(self.get_current().get_ra(), self.get_current().get_dec())}")
        self.logger.info(f"Цель (RA/Dec): {ra_target_deg:.4f}° / {dec_target_deg:.4f}°")
        self.logger.info(f"Цель (J2000 RA/Dec): {coordinate_utils.toJ2000(ra_target_deg, dec_target_deg)}")
        self.logger.info(f"Целевые углы моторов: RA(h)={target_motor_ra:.4f}°, Dec(v)={target_motor_dec:.4f}°")
        self.logger.info(f"Текущие углы моторов: RA(h)={current_motor_ra:.4f}°, Dec(v)={current_motor_dec:.4f}°")
        self.logger.info(f"RA: текущий={current_motor_ra:.2f}, цель={target_motor_ra:.2f}")
        self.logger.info(f"Dec: текущий={current_motor_dec:.2f}, цель={target_motor_dec:.2f}")
        self.logger.info(f"Относительный поворот: RA(h)={delta_ra:.4f}°, Dec(v)={delta_dec:.4f}°")

        self.mouth.goto(SkyCoordinate(delta_ra, delta_dec))

        self.mouth.current = SkyCoordinate(target_motor_ra, target_motor_dec)

        self.mouth.goto_in_progress = False
        return Command.END

    def goto_az_alt_prec(self, data):
        return self.goto_ra_dec(data, True)

    def goto_az_alt(self, data, precise: bool = False):
        self.logger.info(f"Старт команды GOTO Az/Alt (точный режим: {precise})")
        self.mouth.goto_in_progress = True

        az_alt = strip_command_letter(data)
        az_alt_arr = az_alt.split(',')

        # Координаты в J2000
        az_target_deg = astropi_utils.hex_to_degrees(az_alt_arr[0], precise)
        alt_target_deg = astropi_utils.hex_to_degrees(az_alt_arr[1], precise)

        # Целевые углы моторов
        target_motor_az = astropi_utils.normalize_degrees_unsigned(az_target_deg + 180.0) # [0, 360)
        target_motor_alt = alt_target_deg # - 360.0  # Dec — прямой угол [-90, 90]

        # Текущие углы моторов
        current_motor_az = self.mouth.motor_h_angle
        current_motor_alt = self.mouth.motor_v_angle

        delta_az = current_motor_az - (self.get_current().get_az() - target_motor_az)
        delta_alt = current_motor_alt - (self.get_current().get_alt() - target_motor_alt)

        self.logger.info(f"Текущая цель (Az/Alt): {self.get_current().get_ra():.4f}° / {self.get_current().get_dec():.4f}°")
        self.logger.info(f"Цель (Az/Alt): {az_target_deg:.4f}° / {alt_target_deg:.4f}°")
        self.logger.info(f"Целевые углы моторов: Az(h)={target_motor_az:.4f}°, Alt(v)={target_motor_alt:.4f}°")
        self.logger.info(f"Текущие углы моторов: Az(h)={current_motor_az:.4f}°, Alt(v)={current_motor_alt:.4f}°")
        self.logger.info(f"Относительный поворот: Az(h)={delta_az:.4f}°, Alt(v)={delta_alt:.4f}°")

        self.mouth.goto(SkyCoordinate(delta_az, delta_alt))

        self.mouth.current = SkyCoordinate(target_motor_az, target_motor_alt)

        self.mouth.goto_in_progress = False
        return Command.END
