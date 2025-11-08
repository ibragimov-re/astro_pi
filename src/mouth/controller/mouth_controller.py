import sys
import threading

from src.motor.motor_list import MOTORS
from src.mouth.mouth import Mouth
from src.utils.app_logger import AppLogger

MAX_SPEED = 10
HIGH_SPEED = 5
MID_SPEED = 3
LOW_SPEED = 1

CURRENT_MOTOR = MOTORS.get('NEMA17')

# двигатель Ra
PIN_DIR_RA = "PD22"     # 7 зеленый
PIN_STEP_RA = "PD25"    # 5 синий
PIN_ENABLE_RA = "PD26"  # 3 фиолетовый
PIN_MS_ALL_RA = "PL2"   # 8 синий

# пины двигателя Dec
PIN_DIR_DEC = "PD16"      # 18 зеленый
PIN_STEP_DEC = "PD15"     # 16 синий
PIN_ENABLE_DEC = "PD18"   # 12 фиолетовый
PIN_MS_ALL_DEC = "PL3"    # 10 сиреневый

LOG = AppLogger.info("MouthEqController")


class MouthEqController:

    def __init__(self, mouth_params: Mouth, motor_type):
        self.logger = AppLogger.info(mouth_params.name)

        self.logger.info(f"Инициализация монтировки: {mouth_params.name}")
        self.mouth = mouth_params

        self.logger.info(f"Инициализация двигателя прямого восхождения (Ra): {CURRENT_MOTOR.name}")
        self.motorRa = self._create_motor_controller_ra(motor_type)

        self.logger.info(f"Инициализация двигателя склонения (Dec): {CURRENT_MOTOR.name}")
        self.motorDec = self._create_motor_controller_dec(motor_type)

        self.curr_ra = 0.0
        self.curr_dec = 0.0
        self.last_ra = 0.0
        self.last_dec = 0.0

    def _create_motor_controller_dec(self, motor_type):
        return self._create_motor_controller(motor_type, CURRENT_MOTOR, PIN_STEP_DEC, PIN_DIR_DEC, PIN_ENABLE_DEC,
                                             [PIN_MS_ALL_DEC, PIN_MS_ALL_DEC, PIN_MS_ALL_DEC])

    def _create_motor_controller_ra(self, motor_type):
        return self._create_motor_controller(motor_type, CURRENT_MOTOR, PIN_STEP_RA, PIN_DIR_RA, PIN_ENABLE_RA,
                                             [PIN_MS_ALL_RA, PIN_MS_ALL_RA, PIN_MS_ALL_RA])

    def _create_motor_controller(self, motor_type, motor_params, step_pin, dir_pin, enable_pin=None, ms_pins=None):
        if motor_type == "real":
            self.logger.info("Выбран реальный тип контроллера A4988")
            try:
                from src.motor.controller.a4988_motor_controller import A4988MotorController
                return A4988MotorController(motor_params, step_pin, dir_pin, enable_pin, ms_pins)
            except ImportError as e:
                self.logger.error(
                    "Ошибка: A4988 контроллер недоступен. Убедитесь, что установлены зависимости (например, OPi.GPIO).",
                    file=sys.stderr)
                sys.exit(1)
        elif motor_type == "sim":
            self.logger.info("Выбран симулятор контроллера")
            from src.motor.controller.sim_motor_controller import SimMotorController
            return SimMotorController(motor_params, step_pin, dir_pin, enable_pin, ms_pins)
        else:
            self.logger.critical(f"Неизвестный тип мотор-контроллера: {motor_type}")
            raise ValueError(f"Invalid motor type: {motor_type}")

    def goto(self, ra, dec):
        try:
            self.logger.info(f"Инициализация поворота: {ra}°, {dec}°")

            # Создаем потоки для каждого двигателя
            thread1 = threading.Thread(target=self.move_motor_sync, args=(self.motorRa, ra, MAX_SPEED))
            thread2 = threading.Thread(target=self.move_motor_sync, args=(self.motorDec, dec, MAX_SPEED))

            # Запускаем потоки одновременно
            thread1.start()
            thread2.start()

            # Ждем завершения обоих потоков
            thread1.join()
            thread2.join()

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")

        return {self.curr_ra, self.curr_dec}

    def move_motor_sync(self, motor, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        motor.move_degrees(angle, speed)
