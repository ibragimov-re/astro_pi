from src.motor.motor import Motor
from src.motor.pins.motor_pins import MotorPins
from src.mount.mount import Mount
from src.mount.tracking_mode import TrackingMode
from src.utils.app_logger import AppLogger
from src.utils.location import SkyCoordinate, Location

MAX_SPEED = 10
HIGH_SPEED = 5
MID_SPEED = 3
LOW_SPEED = 1

class MountController:
    def __init__(self, mount_params: Mount, motor_params: Motor, pins_h: MotorPins, pins_v: MotorPins,
                 motor_h_index: str, motor_v_index: str):
        self.logger = AppLogger.info(mount_params.name)

        self.logger.info(f"Инициализация монтировки: {mount_params.name}")
        self.params = mount_params
        self.motor_params = motor_params

        self.pins_v = pins_v
        self.pins_h = pins_h

        self.motor_v = self.create_motor_v_controller(motor_params, self.pins_v, motor_v_index)
        self.motor_h = self.create_motor_h_controller(motor_params, self.pins_h, motor_h_index)

        self.location = Location.zero_north_east()

        self.sync = SkyCoordinate.zero()
        self.current = SkyCoordinate.zero()

        # # Ra, Az
        # self.last_h = self.curr_h = target.ra_az if len(target) >= 1 else 0.0
        # # Dec, Alt
        # self.last_v = self.curr_v = target.dec_alt if len(target) >= 2 else 0.0

        self.goto_in_progress = False

    def set_sync(self, target: SkyCoordinate):
        self.current = SkyCoordinate(target.get_horizontal(), target.get_vertical())

    def set_location(self, location: Location):
        self.location = location

    def create_motor_v_controller(self, motor_params, pins, motor_index):
        raise NotImplementedError("Мотор вертикали не проинициализирован")

    def create_motor_h_controller(self, motor_params, pins, motor_index):
        raise NotImplementedError("Мотор горизонтали не проинициализирован")

    def get_mount_tracking_type(self) -> TrackingMode:
        return self.params.tracking_mode

    def goto(self, target: SkyCoordinate, speed=MAX_SPEED):
        try:
            self.logger.info(f"Инициализация поворота: по вертикали: {target.get_vertical():.4f}°, по горизонтали: {target.get_horizontal():.4f}°")

            self.goto_in_progress = True
            self.move_motor_v(target.get_vertical(), speed)
            self.move_motor_h(target.get_horizontal(), speed)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")
        finally:
            self.goto_in_progress = False

        return self.current

    def move_motor_v(self, angle, speed=HIGH_SPEED):
        """Функция для движения двигателя по вертикали"""
        if speed <= 0:
            return
        self.motor_v.move_degrees(angle, speed)
        self.current.dec_alt_v = angle

    def move_motor_h(self, angle, speed=HIGH_SPEED):
        """Функция для движения двигателя по горизонтали"""
        if speed <= 0:
            return
        self.motor_h.move_degrees(angle, speed)
        self.current.ra_az_h = angle


    def slew_motor_v(self, angle, speed=HIGH_SPEED):
        """Функция для сдвига двигателя по вертикали"""
        if speed <= 0:
            return
        self.motor_v.move_degrees(angle, speed)
        self.current.dec_alt_v += angle

    def slew_motor_h(self, angle, speed=HIGH_SPEED):
        """Функция для сдвига двигателя по горизонтали"""
        if speed <= 0:
            return
        self.motor_h.move_degrees(angle, speed)
        self.current.ra_az_h += angle
