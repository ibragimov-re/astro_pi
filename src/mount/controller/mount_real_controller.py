import sys
import threading

from src.motor.motor import Motor
from src.motor.pins.a4988_motor_pins import A4988MotorPins
from src.mount.controller.mount_controller import MountController
from src.mount.mount import Mount
from src.mount.tracking_mode import TrackingMode
from src.utils.location import SkyCoordinate

MAX_SPEED = 2
HIGH_SPEED = 5
MID_SPEED = 3
LOW_SPEED = 1

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


class MountRealController(MountController):
    def __init__(self, mount_params: Mount, motor_params: Motor, motor_h_index, motor_v_index):
        super().__init__(mount_params, motor_params,
                         A4988MotorPins(PIN_STEP_RA, PIN_DIR_RA, PIN_ENABLE_RA, [PIN_MS_ALL_RA, PIN_MS_ALL_RA, PIN_MS_ALL_RA]),
                         A4988MotorPins(PIN_STEP_DEC, PIN_DIR_DEC, PIN_ENABLE_DEC, [PIN_MS_ALL_DEC, PIN_MS_ALL_DEC, PIN_MS_ALL_DEC]),
                         motor_h_index, motor_v_index)

    def create_motor_v_controller(self, motor_params, pins, motor_index):
        axis = "Alt" if self.get_mount_tracking_type() == TrackingMode.ALT_AZ else "Dec"
        self.logger.info("")
        self.logger.info(f"Инициализация двигателя прямого восхождения ({axis})")

        return self.create_motor_controller(axis, motor_params, pins, motor_index)

    def create_motor_h_controller(self, motor_params, pins, motor_index):
        axis = "Az" if self.get_mount_tracking_type() == TrackingMode.ALT_AZ else "Ra"
        self.logger.info("")
        self.logger.info(f"Инициализация двигателя склонения ({axis})")

        return self.create_motor_controller(axis, motor_params, pins, motor_index)

    def create_motor_controller(self, axis, motor_params, pins, motor_index=None):
            self.logger.info("Выбран реальный тип контроллера A4988")
            try:
                import OPi.GPIO as GPIO
                from src.motor.controller.step_motor_controller import StepMotorController
                return StepMotorController(motor_params, pins, GPIO, axis)
            except ImportError as e:
                self.logger.error(
                    "Ошибка: A4988 контроллер недоступен. Убедитесь, что установлены зависимости (например, OPi.GPIO) или запуститесь в режиме симуляции")
                sys.exit(1)

    def goto(self, target: SkyCoordinate, speed=MAX_SPEED):
        try:
            self.logger.info(
                f"Инициализация поворота: по вертикали: {target.get_vertical():.4f}°, по горизонтали: {target.get_horizontal():.4f}°")

            self.goto_in_progress = True

            # Создаем потоки для каждого двигателя
            thread_ra = threading.Thread(target=super().move_motor_h, args=(target.get_horizontal(), speed))
            thread_dec = threading.Thread(target=super().move_motor_v, args=(target.get_vertical(), speed))

            # Запускаем потоки одновременно
            thread_ra.start()
            thread_dec.start()

            # Ждем завершения обоих потоков
            thread_ra.join()
            thread_dec.join()

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")
        finally:
            self.goto_in_progress = False

        return self.current
