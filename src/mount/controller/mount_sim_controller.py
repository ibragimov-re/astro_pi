import kopis as GPIO

from src.motor.controller.sim_motor_controller import SimMotorController
from src.motor.motor import Motor
from src.mount.controller.mount_real_controller import MountRealController
from src.mount.mount import Mount
from src.mount.tracking_mode import TrackingMode
from src.utils.location import SkyCoordinate, Location

MAX_SPEED = 10

class MountSimController(MountRealController):

    def __init__(self, mount_params: Mount, motor_params: Motor):
        super().__init__(mount_params, motor_params, '#Nema17HS8401_Horizontal', '#Nema17HS8401_Vertical')

        mount_type = GPIO.kopis_motorsim.AZ if self.get_mount_tracking_type() == TrackingMode.ALT_AZ else GPIO.kopis_motorsim.EQ
        GPIO.kopis_motorsim.setup_motors_by_mount_type(mount_type)
        self.logger.info(f"Для симулятора выбран тип монтировки: {mount_type}")

    def create_motor_controller(self, axis, motor_params, pins, motor_index = None):
        return SimMotorController(motor_params, pins, GPIO, motor_index, axis)

    def goto(self, target: SkyCoordinate, speed=MAX_SPEED):
        try:
            self.logger.info(
                f"Инициализация поворота: по вертикали: {target.get_vertical():.4f}°, по горизонтали: {target.get_horizontal():.4f}°")

            self.goto_in_progress = True

            super().move_motor_h(target.get_horizontal(), speed)
            super().move_motor_v(target.get_vertical(), speed)

            self.logger.info("Оба двигателя завершили движение")
        except ValueError:
            self.logger.error("Ошибка ввода! Попробуйте снова.")
        except KeyboardInterrupt:
            self.logger.warn("Прервано пользователем")
        finally:
            self.goto_in_progress = False

        return self.current
