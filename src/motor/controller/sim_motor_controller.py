#!/usr/bin/env python3
from typing import override

from src.motor.motor import Motor
from src.motor.pins.a4988_motor_pins import A4988MotorPins
from src.motor.controller.step_motor_controller import StepMotorController


class SimMotorController(StepMotorController):
    """Контроллер для симулятора двигателя"""
    def __init__(self, motor_params: Motor, pins: A4988MotorPins, gpio_lib, motor_index, axis):
        super().__init__(motor_params, pins, gpio_lib, axis, motor_index)

    @override
    def move_degrees(self, degrees, speed=5):
        """Поворот на заданное количество градусов"""
        self.activate()

        self.logger.info(f"Поворот по оси ({self.axis}) на {degrees:.2f}°")
        self.gpio.kopis_motorsim.move_degrees(self.motor_index, degrees, speed)

        self.deactivate()
