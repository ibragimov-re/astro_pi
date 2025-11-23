import copy

from src.motor.motor import Motor
from src.motor.pins.motor_pins import MotorPins
from src.mouth.mouth import Mouth
from src.mouth.tracking_mode import TrackingMode
from src.utils.app_logger import AppLogger
from src.utils.location import SkyCoordinate

MAX_SPEED = 10
HIGH_SPEED = 5


class MouthController:
    def __init__(self, mouth_params: Mouth, motor_params: Motor, target: SkyCoordinate, pins_h: MotorPins, pins_v: MotorPins,
                 motor_h_index: str, motor_v_index: str):
        self.logger = AppLogger.info(mouth_params.name)

        self.logger.info(f"Инициализация монтировки: {mouth_params.name}")
        self.params = mouth_params
        self.motor_params = motor_params

        self.pins_v = pins_v
        self.pins_h = pins_h

        self.motor_v = self.create_motor_v_controller(motor_params, self.pins_v, motor_v_index)
        self.motor_h = self.create_motor_h_controller(motor_params, self.pins_h, motor_h_index)

        self.sync = copy.copy(target)
        self.current = target

        # # Ra, Az
        # self.last_h = self.curr_h = target.ra_az if len(target) >= 1 else 0.0
        # # Dec, Alt
        # self.last_v = self.curr_v = target.dec_alt if len(target) >= 2 else 0.0

        self.goto_in_progress = False

    def set_sync(self, target):
        self.sync = target

    def create_motor_v_controller(self, motor_params, pins, motor_index):
        raise NotImplementedError("Мотор вертикали не проинициализирован")

    def create_motor_h_controller(self, motor_params, pins, motor_index):
        raise NotImplementedError("Мотор горизонтали не проинициализирован")

    def get_mouth_tracking_type(self) -> TrackingMode:
        return self.params.tracking_mode

    def goto(self, target: SkyCoordinate):
        try:
            self.logger.info(f"Инициализация поворота: по вертикали: {target.get_vertical():.4f}°, по горизонтали: {target.get_horizontal():.4f}°")

            self.goto_in_progress = True
            self.move_motor_v(target.get_vertical(), MAX_SPEED)
            self.move_motor_h(target.get_horizontal(), MAX_SPEED)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")
        finally:
            self.goto_in_progress = False

        return self.current

    def move_motor_v(self, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        self.motor_v.move_degrees(angle, speed)

    def move_motor_h(self, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        self.motor_h.move_degrees(angle, speed)
