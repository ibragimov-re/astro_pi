#!/usr/bin/env python3

import OPi.GPIO as GPIO

from base_motor_controller import BaseMotorController


class ULN2003Controller(BaseMotorController):
    """Контроллер для драйвера ULN2003"""

    def __init__(self, motor_params, in1, in2, in3, in4):
        super().__init__(motor_params)
        self.pins = [in1, in2, in3, in4]
        self.current_sequence = 'half'

        # Настройка GPIO
        GPIO.setmode(GPIO.SUNXI)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Последовательности шагов
        self.sequences = {
            'full': {
                'steps': [[1, 1, 0, 0],
                          [0, 1, 1, 0],
                          [0, 0, 1, 1],
                          [1, 0, 0, 1]],
                'min_delay': 0.005, 'max_delay': 0.02
            },
            'half': {
                'steps': [[1, 0, 0, 0],
                          [1, 1, 0, 0],
                          [0, 1, 0, 0],
                          [0, 1, 1, 0],
                          [0, 0, 1, 0],
                          [0, 0, 1, 1],
                          [0, 0, 0, 1],
                          [1, 0, 0, 1]],
                'min_delay': 0.001, 'max_delay': 0.01
            }
        }

        self.current_step = 0
        self.set_sequence('half')

    def set_sequence(self, seq_type='half'):
        """Выбор режима работы"""
        self.current_sequence = seq_type
        self.sequence = self.sequences[seq_type]['steps']
        self.step_count = len(self.sequence)
        self.MIN_DELAY = self.sequences[seq_type]['min_delay']
        self.MAX_DELAY = self.sequences[seq_type]['max_delay']
        print(f"Режим: {seq_type}, задержки: {self.MIN_DELAY}-{self.MAX_DELAY} сек")

    def activate(self):
        if not self.is_active:
            self.is_active = True
            print("Двигатель активирован")

    def deactivate(self):
        if self.is_active:
            self._set_pins([0, 0, 0, 0])
            self.is_active = False
            print("Двигатель деактивирован")

    def perform_step(self, direction):
        self.current_step = (self.current_step + direction) % self.step_count
        self._set_pins(self.sequence[self.current_step])

    def _calculate_delay(self, speed):
        if self.current_sequence == 'full':
            return self.MAX_DELAY - (speed - 1) * (self.MAX_DELAY - self.MIN_DELAY) / 9
        else:
            return self.MAX_DELAY - (speed - 1) * (self.MAX_DELAY - self.MIN_DELAY) / 9

    def _set_pins(self, values):
        for pin, value in zip(self.pins, values):
            GPIO.output(pin, value)

    def release(self):
        self.deactivate()
        GPIO.cleanup()
        print("Двигатель полностью отключен")