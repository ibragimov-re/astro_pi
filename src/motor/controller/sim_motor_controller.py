#!/usr/bin/env python3

import threading
import time

from motor.motor import Motor
from src.utils.app_logger import AppLogger

LOGGER = AppLogger.info("SimMotorController")


class SimMotorController:
    """Контроллер для симулятора двигателя"""

    def __init__(self, motor_params: Motor, step_pin, dir_pin, enable_pin=None, ms_pins=None):

        self.motor_params = motor_params

        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.ms_pins = ms_pins

        # Блокировка для потокобезопасности
        self.lock = threading.Lock()

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

        if self.ms_pins:
            self.set_microstep(16)  # 1/16 по умолчанию
        else:
            LOGGER.info("Микрошаг не настроен (не заданы MS пины)")

        self.is_active = False

    def set_microstep(self, divisor):
        LOGGER.info(f"Установлен микрошаг: 1/{divisor}")

    def move_degrees(self, degrees, speed=5):
        """Поворот на заданное количество градусов"""
        with self.lock:  # thread safety
            self.activate()

            # Расчет шагов с учетом микрошага
            steps = int((degrees / 360.0) * self.motor_params.steps_per_turn * self.microstep_divisor)

            direction = "по часовой" if steps >= 0 else "против часовой"
            LOGGER.info(f"Поворот на {degrees}° ({abs(steps)} шагов, {direction})")
            LOGGER.info(f"Микрошаг: 1/{self.microstep_divisor}, Скорость: {speed}")

            self.move(steps, speed)
            self.deactivate()

    def move(self, steps, speed=5):
        """Движение на указанное количество шагов"""
        if steps == 0:
            return

        speed = self.motor_params.max_speed if speed > self.motor_params.max_speed else speed

        direction = 1 if steps >= 0 else -1
        steps_abs = abs(steps)

        # Расчет задержки
        min_delay = 0.001  # Увеличил для надежности
        max_delay = 0.02  # Увеличил для надежности
        base_delay = max_delay - (speed - 1) * (max_delay - min_delay) / 9

        LOGGER.info(f"Задержка на шаг: {base_delay:.6f} сек")

        start_time = time.time()

        # Генерация импульсов
        for i in range(steps_abs):
            time.sleep(base_delay / 2)
            time.sleep(base_delay / 2)

            # Прогресс каждые 10%
            if steps_abs > 10 and i % (steps_abs // 10) == 0:
                progress = (i / steps_abs) * 100
                elapsed = time.time() - start_time
                LOGGER.info(f"Выполнено: {progress:.1f}% ({i}/{steps_abs} шагов, {elapsed:.2f} сек)")

        LOGGER.info(f"Движение завершено. Время: {time.time() - start_time:.2f} сек")

    def activate(self):
        """Включение драйвера"""
        if not self.is_active:
            self.is_active = True
            LOGGER.info("Драйвер включен")

    def deactivate(self):
        """Выключение драйвера"""
        if self.is_active:
            self.is_active = False
            LOGGER.info("Драйвер выключен")

    def release(self):
        """Освобождение ресурсов"""
        self.deactivate()
        LOGGER.info("Контроллер полностью отключен")

    def in_progress(self):
        return self.is_active
