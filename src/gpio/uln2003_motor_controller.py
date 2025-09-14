#!/usr/bin/env python3

import OPi.GPIO as GPIO
from base_motor_controller import BaseMotorController


class ULN2003Controller(BaseMotorController):
    """Контроллер для драйвера ULN2003"""

    def __init__(self, motor_params, in1, in2, in3, in4):
        super().__init__(motor_params)
        self.pins = [in1, in2, in3, in4]

        # Настройка GPIO
        GPIO.setmode(GPIO.SUNXI)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        self.current_step = 0

    def _apply_step_pattern(self, pattern):
        """Применение pattern к пинам ULN2003"""
        for pin, value in zip(self.pins, pattern):
            GPIO.output(pin, value)

    def deactivate(self):
        """Деактивация с отключением всех катушек"""
        if self.is_active:
            self._apply_step_pattern([0, 0, 0, 0])
            super().deactivate()

    def release(self):
        self.deactivate()
        GPIO.cleanup()
        print("Двигатель ULN2003 полностью отключен")