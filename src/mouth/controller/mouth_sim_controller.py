from src.motor.motor import Motor
from src.mouth.controller.mouth_controller import MouthController
from src.mouth.mouth import Mouth
from src.utils.app_logger import AppLogger

MAX_SPEED = 10

# пины двигателя Vertical
PIN_DIR_V = "PD22"
PIN_STEP_V = "PD25"
PIN_ENABLE_V = "PD26"
PIN_MS_ALL_V = "PL2"

# пины двигателя Horizontal
PIN_DIR_H = "PD16"
PIN_STEP_H = "PD15"
PIN_ENABLE_H = "PD18"
PIN_MS_ALL_H = "PL3"


class MouthSimController(MouthController):

    def __init__(self, mouth_params: Mouth, motor_params: Motor):
        super().__init__(mouth_params, motor_params, "sim",
                         PIN_STEP_V, PIN_DIR_V, PIN_ENABLE_V, [PIN_MS_ALL_V, PIN_MS_ALL_V, PIN_MS_ALL_V],
                         PIN_STEP_H, PIN_DIR_H, PIN_ENABLE_H, [PIN_MS_ALL_H, PIN_MS_ALL_H, PIN_MS_ALL_H])
        self.logger = AppLogger.info(mouth_params.name)

    def goto(self, vert, horizont):
        try:
            self.logger.info(f"Инициализация поворота: {vert}°, {horizont}°")

            super().move_motor_v_sync(vert, MAX_SPEED)
            super().move_motor_h_sync(horizont, MAX_SPEED)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")

        return {self.curr_v, self.curr_h}
