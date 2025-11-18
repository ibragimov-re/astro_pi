import threading

from motor.motor import Motor
from mouth.controller.mouth_controller import MouthController
from src.motor.motor_list import MOTORS
from src.mouth.mouth import Mouth
from utils.app_logger import AppLogger

MAX_SPEED = 10
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


class MouthEqController(MouthController):
    def __init__(self, mouth_params: Mouth, motor_params: Motor, motor_type):
        super().__init__(mouth_params, motor_params, motor_type,
                         PIN_STEP_RA, PIN_DIR_RA, PIN_ENABLE_RA, [PIN_MS_ALL_RA, PIN_MS_ALL_RA, PIN_MS_ALL_RA],
                         PIN_STEP_DEC, PIN_DIR_DEC, PIN_ENABLE_DEC, [PIN_MS_ALL_DEC, PIN_MS_ALL_DEC, PIN_MS_ALL_DEC])
        self.logger = AppLogger.info(mouth_params.name)
        # self.curr_ra = 0.0
        # self.curr_dec = 0.0
        # self.last_ra = 0.0
        # self.last_dec = 0.0

    def goto(self, ra, dec):
        try:
            super().logger.info(f"Инициализация поворота: {ra}°, {dec}°")

            # Создаем потоки для каждого двигателя
            thread_ra = threading.Thread(target=super().move_motor_v_sync, args=(ra, MAX_SPEED))
            thread_dec = threading.Thread(target=super().move_motor_h_sync, args=(dec, MAX_SPEED))

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

        return {super().curr_v, super().curr_h}
