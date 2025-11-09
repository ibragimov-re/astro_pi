#!/usr/bin/env python3

import threading
import time

import OPi.GPIO as GPIO

from src.utils.app_logger import AppLogger

LOGGER = AppLogger.info("A4988MotorController")


class A4988MotorController:
    """Контроллер для драйвера A4988"""

    def __init__(self, motor_params, step_pin, dir_pin, enable_pin=None, ms_pins=None):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.SUNXI)

        self.motor_params = motor_params

        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.ms_pins = ms_pins

        # Блокировка для потокобезопасности
        self.lock = threading.Lock()

        # Настройка пинов GPIO
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.output(self.step_pin, GPIO.LOW)
        GPIO.output(self.dir_pin, GPIO.LOW)

        if self.enable_pin:
            GPIO.setup(self.enable_pin, GPIO.OUT)
            GPIO.output(self.enable_pin, GPIO.HIGH)  # Выключено по умолчанию

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
            GPIO.setup(self.ms_pins[0], GPIO.OUT)

            # сейчас у нас нет свободных gpio что бы подключить все пины MS обоих двигателей
            # for pin in self.ms_pins:
            #     GPIO.setup(pin, GPIO.OUT)

            self.set_microstep(16)  # 1/16 по умолчанию
        else:
            LOGGER.info("Микрошаг не настроен (не заданы MS пины)")

        self.is_active = False

        LOGGER.info(f"Инициализирован A4988 для: {self.motor_params.name}")
        LOGGER.info(f"Микрошаг: 1/{self.microstep_divisor}")

    def set_microstep(self, divisor):
        """Установка микрошага"""
        if divisor in self.microstep_config and self.ms_pins:
            for pin, value in zip(self.ms_pins, self.microstep_config[divisor]):
                GPIO.output(pin, value)
            self.microstep_divisor = divisor
            LOGGER.info(f"Установлен микрошаг: 1/{divisor}")
        else:
            LOGGER.info(f"Невозможно установить микрошаг 1/{divisor}")

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

        # Установка направления
        GPIO.output(self.dir_pin, GPIO.HIGH if direction > 0 else GPIO.LOW)

        # Расчет задержки
        min_delay = 0.001  # Увеличил для надежности
        max_delay = 0.02  # Увеличил для надежности
        base_delay = max_delay - (speed - 1) * (max_delay - min_delay) / 9

        LOGGER.info(f"Задержка на шаг: {base_delay:.6f} сек")

        start_time = time.time()

        # Генерация импульсов
        for i in range(steps_abs):
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(base_delay / 2)
            GPIO.output(self.step_pin, GPIO.LOW)
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
            if self.enable_pin:
                GPIO.output(self.enable_pin, GPIO.LOW)
            self.is_active = True
            LOGGER.info("Драйвер включен")

    def deactivate(self):
        """Выключение драйвера"""
        if self.is_active:
            if self.enable_pin:
                GPIO.output(self.enable_pin, GPIO.HIGH)
            self.is_active = False
            LOGGER.info("Драйвер выключен")

    def release(self):
        """Освобождение ресурсов"""
        self.deactivate()
        GPIO.cleanup()
        LOGGER.info("Контроллер полностью отключен")

    def in_progress(self):
        return self.is_active
