#!/usr/bin/env python3

import time

import OPi.GPIO as GPIO

PROGRESS_OUTPUT_TIMEOUT = 0.5   # С какой частотой в секундах выводит прогресс по вращению


class MotorController:
    def __init__(self, motor_params, in1, in2, in3, in4):
        self.pins = [in1, in2, in3, in4]
        self.is_active = False
        self.current_sequence = 'half'  # По умолчанию полушаговый режим (более плавный)
        self.motor_params = motor_params
        print(f"Инициализирован двигатель: {self.motor_params.name}")
        print(f"Шагов на оборот: {self.motor_params.steps_per_turn:.0f}")
        print(f"Коэффициент редукции: 1 / {(self.motor_params.steps_per_turn * self.motor_params.speed_variation_ratio):.000f}")

        # Задаем пины в архитектурном формате (пример: "PD22")
        GPIO.setmode(GPIO.SUNXI)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Последовательности шагов. Для full режима нужны большие задержки
        self.sequences = {
            'full': {
                'steps': [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
                ],
                'min_delay': 0.005,
                'max_delay': 0.02
            },
            'half': {
                'steps': [
                    [1, 0, 0, 0],
                    [1, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 0],
                    [0, 0, 1, 1],
                    [0, 0, 0, 1],
                    [1, 0, 0, 1]
                ],
                'min_delay': 0.001,
                'max_delay': 0.01
            }
        }

        self.current_step = 0
        self.set_sequence('half')  # Полушаговый режим по дефолту

    def set_sequence(self, seq_type='half'):
        """Выбор режима работы: 'full' или 'half'"""
        self.current_sequence = seq_type
        self.sequence = self.sequences[seq_type]['steps']
        self.step_count = len(self.sequence)

        # Устанавливаем соответствующие задержки для режима
        if seq_type == 'full':
            self.MIN_DELAY = self.sequences['full']['min_delay']
            self.MAX_DELAY = self.sequences['full']['max_delay']
        else:
            self.MIN_DELAY = self.sequences['half']['min_delay']
            self.MAX_DELAY = self.sequences['half']['max_delay']

        print(f"Установлен режим: {seq_type} ({self.step_count} шагов на цикл)")
        print(f"Задержки: {self.MIN_DELAY}-{self.MAX_DELAY} сек")

    def activate(self):
        """Активация двигателя"""
        if not self.is_active:
            print("Двигатель активирован")
            self.is_active = True

    def deactivate(self):
        """Деактивация двигателя"""
        if self.is_active:
            self._set_pins([0, 0, 0, 0])
            print("Двигатель деактивирован")
            self.is_active = False

    def move_degrees(self, degrees, speed=5):
        """
        Поворот на заданное количество градусов
        degrees: угол в градусах со знаком
        speed: скорость (1-10), где 1 - медленно, 10 - быстро
        """
        self.activate()

        # Используем параметры двигателя для расчета шагов
        steps = self.motor_params.steps_for_degrees(degrees)

        direction = "по часовой" if steps >= 0 else "против часовой"
        print(f"Поворот на {degrees}° ({abs(steps)} шагов, {direction})")
        print(f"Режим: {self.current_sequence}, Скорость: {speed}")

        self.move(steps, speed=speed)
        self.deactivate()

    def move(self, steps, speed=5):
        """
        Движение на указанное количество шагов
        steps: количество шагов (+ по часовой, - против часовой)
        speed: скорость (1-10)
        """
        direction = 1 if steps >= 0 else -1
        steps_abs = abs(steps)

        # РАЗНЫЕ формулы задержки для разных режимов
        if self.current_sequence == 'full':
            # Для full режима - более длинные задержки
            base_delay = self.MAX_DELAY - (speed - 1) * (self.MAX_DELAY - self.MIN_DELAY) / 9
        else:
            # Для half режима - более короткие задержки
            base_delay = self.MAX_DELAY - (speed - 1) * (self.MAX_DELAY - self.MIN_DELAY) / 9

        print(f"Задержка на шаг: {base_delay:.4f} сек")

        # Переменные для отслеживания прогресса по времени
        start_time = time.time()
        last_progress_time = start_time
        # Вывод прогресса каждые 0.5 секунды
        for i in range(steps_abs):
            self.current_step = (self.current_step + direction) % self.step_count
            self._set_pins(self.sequence[self.current_step])
            time.sleep(base_delay)

            # Вывод прогресса по времени (каждые 0.5 секунды)
            current_time = time.time()
            if current_time - last_progress_time >= PROGRESS_OUTPUT_TIMEOUT:
                self._print_progress(i, steps_abs, start_time)
                last_progress_time = current_time

        # Вывод финального прогресса
        if steps_abs > 0:
            self._print_progress(steps_abs, steps_abs, start_time)

    def _print_progress(self, current_step, total_steps, start_time):
        """Вывод прогресса выполнения"""
        if total_steps == 0:
            return

        progress_percent = (current_step / total_steps) * 100
        elapsed_time = time.time() - start_time

        # Расчет оставшегося времени
        if current_step > 0:
            steps_per_second = current_step / elapsed_time
            remaining_time = (total_steps - current_step) / steps_per_second
            time_info = f", осталось: {remaining_time:.1f} сек"
        else:
            time_info = ""

        print(f"Выполнено: {progress_percent:.1f}% ({current_step}/{total_steps} шагов{time_info})")

    def _set_pins(self, values):
        """Установка состояний пинов"""
        for pin, value in zip(self.pins, values):
            GPIO.output(pin, value)

    def release(self):
        """Полное отключение"""
        self.deactivate()
        GPIO.cleanup()
        print("Двигатель полностью отключен")
