#!/usr/bin/env python3

import threading
import time

from src.motor.motor import Motor
from motor.pins.a4988_motor_pins import A4988MotorPins
from src.utils.app_logger import AppLogger

class StepMotorController:
    """Контроллер для драйвера A4988"""

    def __init__(self, motor_params: Motor, pins: A4988MotorPins, gpio_lib, axis, motor_index=None):
        self.logger = AppLogger.info(motor_params.name)

        self.axis = axis
        self.motor_index = motor_index
        self.motor_params = motor_params

        self.pins = pins

        self.gpio = gpio_lib
        self.gpio.setwarnings(False)
        self.gpio.setmode(self.gpio.SUNXI)

        # Блокировка для потокобезопасности
        self.lock = threading.Lock()

        # Настройка пинов GPIO
        self.gpio.setup(self.pins.step, self.gpio.OUT)
        self.gpio.setup(self.pins.dir, self.gpio.OUT)
        self.gpio.output(self.pins.step, self.gpio.LOW)
        self.gpio.output(self.pins.dir, self.gpio.LOW)

        if self.pins.enable:
            self.gpio.setup(self.pins.enable, self.gpio.OUT)
            self.gpio.output(self.pins.enable, self.gpio.HIGH)  # Выключено по умолчанию

        # Конфигурация микрошага
        self.microstep_config = {
            1: [0, 0, 0],  # Full step
            2: [1, 0, 0],  # 1/2 step
            4: [0, 1, 0],  # 1/4 step
            8: [1, 1, 0],  # 1/8 step
            16: [1, 1, 1]  # 1/16 step
        }

        # Инициализация микрошага
        self.microstep_divisor = 1  # Значение по умолчанию

        if self.pins.ms:
            self.gpio.setup(self.pins.ms[0], self.gpio.OUT)

            # сейчас у нас нет свободных gpio что бы подключить все пины MS обоих двигателей
            # for pin in self.ms_pins:
            #     self.gpio.setup(pin, self.gpio.OUT)

            self.set_microstep(16)  # 1/16 по умолчанию
        else:
            self.logger.info("Микрошаг не настроен (не заданы MS пины)")

        self.is_active = False

        self.logger.info(f"Инициализирован шаговый мотор '{self.motor_params.name}' с индексом '{self.motor_index}'")

    def set_microstep(self, divisor):
        """Установка микрошага"""
        if divisor in self.microstep_config and self.pins.ms:
            for pin, value in zip(self.pins.ms, self.microstep_config[divisor]):
                self.gpio.output(pin, value)
            self.microstep_divisor = divisor
            self.logger.info(f"Установлен микрошаг: 1/{divisor}")
        else:
            self.logger.info(f"Невозможно установить микрошаг 1/{divisor}")

    def move_degrees(self, degrees, speed=5):
        """Поворот на заданное количество градусов"""
        with self.lock:  # thread safety
            self.activate()

            # Расчет шагов с учетом микрошага
            steps = self._calculate_steps(degrees)

            direction = "по часовой" if steps >= 0 else "против часовой"
            self.logger.info(f"Поворот на {degrees}° ({abs(steps)} шагов, {direction})")
            self.logger.info(f"Микрошаг: 1/{self.microstep_divisor}, Скорость: {speed}")

            self.move(steps, speed)
            self.deactivate()

    def _calculate_steps(self, degrees):
        steps = int((degrees / 360.0) * self.motor_params.steps_per_turn * self.microstep_divisor)
        return steps

    def move(self, steps, speed=5):
        """Движение на указанное количество шагов"""
        if steps == 0:
            return

        speed = self.motor_params.max_speed if speed > self.motor_params.max_speed else speed

        direction = 1 if steps >= 0 else -1
        steps_abs = abs(steps)

        # Установка направления
        self.gpio.output(self.pins.dir, self.gpio.HIGH if direction > 0 else self.gpio.LOW)

        # Расчет задержки
        min_delay = 0.001  # Увеличил для надежности
        max_delay = 0.02  # Увеличил для надежности
        base_delay = max_delay - (speed - 1) * (max_delay - min_delay) / 9

        self.logger.info(f"Задержка на шаг: {base_delay:.6f} сек")

        start_time = time.time()

        # Генерация импульсов
        for i in range(steps_abs):
            self.gpio.output(self.pins.step, self.gpio.HIGH)
            time.sleep(base_delay / 2)
            self.gpio.output(self.pins.step, self.gpio.LOW)
            time.sleep(base_delay / 2)

            # Прогресс каждые 10%
            if steps_abs > 10 and i % (steps_abs // 10) == 0:
                progress = (i / steps_abs) * 100
                elapsed = time.time() - start_time
                self.logger.info(f"Выполнено: {progress:.1f}% ({i}/{steps_abs} шагов, {elapsed:.2f} сек)")

        self.logger.info(f"Движение завершено. Время: {time.time() - start_time:.2f} сек")

    def activate(self):
        """Включение драйвера"""
        if not self.is_active:
            if self.pins.enable:
                self.gpio.output(self.pins.enable, self.gpio.LOW)
            self.is_active = True
            # self.logger.debug("Драйвер включен")

    def deactivate(self):
        """Выключение драйвера"""
        if self.is_active:
            if self.pins.enable:
                self.gpio.output(self.pins.enable, self.gpio.HIGH)
            self.is_active = False
            # self.logger.debug("Драйвер выключен")

    def release(self):
        """Освобождение ресурсов"""
        self.deactivate()
        self.gpio.cleanup()
        # self.logger.debug("Контроллер полностью отключен")

    def in_progress(self):
        return self.is_active
