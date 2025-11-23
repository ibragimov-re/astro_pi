import kopis as GPIO

from src.motor.controller.sim_motor_controller import SimMotorController
from src.motor.motor import Motor
from src.mouth.controller.mouth_real_controller import MouthRealController
from src.mouth.mouth import Mouth
from src.mouth.tracking_mode import TrackingMode
from src.utils.location import SkyCoordinate

MAX_SPEED = 10

class MouthSimController(MouthRealController):

    def __init__(self, mouth_params: Mouth, motor_params: Motor, target: SkyCoordinate):
        super().__init__(mouth_params, motor_params, target, '#Nema17HS8401_Horizontal', '#Nema17HS8401_Vertical')

        mount_type = GPIO.kopis_motorsim.AZ if self.get_mouth_tracking_type() == TrackingMode.ALT_AZ else GPIO.kopis_motorsim.EQ
        GPIO.kopis_motorsim.setup_motors_by_mount_type(mount_type)
        self.logger.info(f"Для симулятора выбран тип монтировки: {mount_type}")

    def create_motor_controller(self, axis, motor_params, pins, motor_index = None):
        return SimMotorController(motor_params, pins, GPIO, motor_index, axis)

    def goto(self, target: SkyCoordinate):
        try:
            self.logger.info(
                f"Инициализация поворота: по вертикали: {target.get_vertical():.4f}°, по горизонтали: {target.get_horizontal():.4f}°")

            self.goto_in_progress = True

            super().move_motor_h(target.get_horizontal(), MAX_SPEED)
            super().move_motor_v(target.get_vertical(), MAX_SPEED)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")
        finally:
            self.goto_in_progress = False

        return self.current
