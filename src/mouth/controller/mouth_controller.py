import sys

from motor.motor import Motor
from mouth.mouth import Mouth
from mouth.tracking_mode import TrackingMode
from utils.app_logger import AppLogger

MAX_SPEED = 10
HIGH_SPEED = 5


class MouthController:
    def __init__(self, mouth_params: Mouth, motor_params: Motor, motor_type,
                 step_v_pin, dir_v_pin, enable_v_pin, ms_v_pins,
                 step_h_pin, dir_h_pin, enable_h_pin, ms_h_pins):
        self.logger = AppLogger.info(mouth_params.name)

        self.logger.info(f"Инициализация монтировки: {mouth_params.name}")
        self.mouth = mouth_params

        self._create_motor_v_controller(dir_v_pin, enable_v_pin, motor_params, motor_type, ms_v_pins, step_v_pin)
        self._create_motor_h_controller(dir_h_pin, enable_h_pin, motor_params, motor_type, ms_h_pins, step_h_pin)

        self.curr_v = 0.0
        self.curr_h = 0.0
        self.last_v = 0.0
        self.last_h = 0.0

    def _create_motor_h_controller(self, dir_h_pin, enable_h_pin, motor_params, motor_type, ms_h_pins, step_h_pin):
        type = "Az" if self.mouth.tracking_mode == TrackingMode.ALT_AZ else "Dec"
        self.logger.info(f"Инициализация двигателя склонения ({type}): {motor_params.name}")


        self.motor_h = self._create_motor_controller(type, motor_type, motor_params, step_h_pin, dir_h_pin, enable_h_pin,
                                                     ms_h_pins)

    def _create_motor_v_controller(self, dir_v_pin, enable_v_pin, motor_params, motor_type, ms_v_pins, step_v_pin):
        type = "Alt" if self.mouth.tracking_mode == TrackingMode.ALT_AZ else "Ra"
        self.logger.info(f"Инициализация двигателя прямого восхождения ({type}): {motor_params.name}")

        self.motor_v = self._create_motor_controller(type, motor_type, motor_params, step_v_pin, dir_v_pin, enable_v_pin,
                                                     ms_v_pins)

    def _create_motor_controller(self, type, motor_type, motor_params, step_pin, dir_pin, enable_pin=None, ms_pins=None):
        if motor_type == "real":
            self.logger.info("Выбран реальный тип контроллера A4988")
            try:
                from src.motor.controller.a4988_motor_controller import A4988MotorController
                return A4988MotorController(motor_params, step_pin, dir_pin, enable_pin, ms_pins)
            except ImportError as e:
                self.logger.error(
                    "Ошибка: A4988 контроллер недоступен. Убедитесь, что установлены зависимости (например, OPi.GPIO) или запуститесь в режиме симуляции",
                    file=sys.stderr)
                sys.exit(1)
        elif motor_type == "sim":
            self.logger.info(f"Для двигателя {type} выбран симулятор контроллера")
            from src.motor.controller.sim_motor_controller import SimMotorController
            return SimMotorController(motor_params, step_pin, dir_pin, enable_pin, ms_pins)
        else:
            self.logger.critical(f"Неизвестный тип мотор-контроллера: {motor_type}")
            raise ValueError(f"Invalid motor type: {motor_type}")

    def goto(self, vert, horizont):
        try:
            self.logger.info(f"Инициализация поворота: {vert}°, {horizont}°")

            self.move_motor_v_sync(vert, MAX_SPEED)
            self.move_motor_h_sync(horizont, MAX_SPEED)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")

        return {self.curr_v, self.curr_h}

    def move_motor_v_sync(self, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        self.motor_v.move_degrees(angle, speed)

    def move_motor_h_sync(self, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        self.motor_h.move_degrees(angle, speed)
