#!/usr/bin/env python3

import time
from abc import abstractmethod

PROGRESS_OUTPUT_TIMEOUT = 0.5


class BaseMotorController:
    """Базовый класс для всех контроллеров шаговых двигателей"""

    # Общие фазы для всех контроллеров
    SEQUENCES = {
        'wave': {  # Однофазный полношаговый (Wave Drive)
            'steps': [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ],
            'min_delay': 0.005,
            'max_delay': 0.02,
            'description': 'Однофазный полношаговый (Wave Drive)'
        },
        'full': {  # Двухфазный полношаговый
            'steps': [
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 1],
                [1, 0, 0, 1]
            ],
            'min_delay': 0.004,
            'max_delay': 0.015,
            'description': 'Двухфазный полношаговый'
        },
        'half': {  # Полушаговый
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
            'max_delay': 0.01,
            'description': 'Полушаговый'
        }
    }

    def __init__(self, motor_params):
        self.motor_params = motor_params
        self.is_active = False
        self.current_sequence = 'half'  # Режим по умолчанию

        print(f"Инициализирован двигатель: {self.motor_params.name}")
        print(f"Шагов на оборот: {self.motor_params.steps_per_turn:.0f}")

        # Инициализация текущей последовательности
        self.set_sequence(self.current_sequence)

    def set_sequence(self, seq_type='half'):
        """Выбор режима работы: 'wave', 'full' или 'half'"""
        if seq_type not in self.SEQUENCES:
            print(f"Режим {seq_type} не поддерживается. Используется 'half'")
            seq_type = 'half'

        self.current_sequence = seq_type
        sequence_data = self.SEQUENCES[seq_type]
        self.sequence = sequence_data['steps']
        self.step_count = len(self.sequence)
        self.MIN_DELAY = sequence_data['min_delay']
        self.MAX_DELAY = sequence_data['max_delay']

        print(f"Установлен режим: {sequence_data['description']}")
        print(f"Шагов на цикл: {self.step_count}, Задержки: {self.MIN_DELAY}-{self.MAX_DELAY} сек")

    def get_available_sequences(self):
        """Возвращает список доступных режимов"""
        return list(self.SEQUENCES.keys())

    def get_sequence_info(self, seq_type):
        """Возвращает информацию о режиме"""
        if seq_type in self.SEQUENCES:
            return self.SEQUENCES[seq_type]['description']
        return "Неизвестный режим"

    def activate(self):
        """Активация двигателя"""
        if not self.is_active:
            self.is_active = True
            print("Двигатель активирован")

    def deactivate(self):
        """Деактивация двигателя"""
        if self.is_active:
            self.is_active = False
            print("Двигатель деактивирован")

    def perform_step(self, direction):
        """Выполнение одного шага"""
        self.current_step = (self.current_step + direction) % self.step_count
        current_pattern = self.sequence[self.current_step]
        self._apply_step_pattern(current_pattern)

    @abstractmethod
    def _apply_step_pattern(self, pattern):
        """Применение pattern к драйверу (должен быть реализован в потомке)"""
        raise NotImplementedError("Метод _apply_step_pattern должен быть реализован в потомке")

    def _calculate_delay(self, speed):
        """Расчет задержки между шагами"""
        return self.MAX_DELAY - (speed - 1) * (self.MAX_DELAY - self.MIN_DELAY) / 9

    def move_degrees(self, degrees, speed=5):
        """Поворот на заданное количество градусов"""
        self.activate()

        steps = self.motor_params.steps_for_degrees(degrees)
        direction_str = "по часовой" if steps >= 0 else "против часовой"

        print(f"Поворот на {degrees} градусов ({abs(steps)} шагов, {direction_str})")
        print(f"Режим: {self.SEQUENCES[self.current_sequence]['description']}")
        print(f"Скорость: {speed}")

        self.move(steps, speed=speed)
        self.deactivate()

    def move(self, steps, speed=5):
        """Движение на указанное количество шагов"""
        if steps == 0:
            return

        direction = 1 if steps >= 0 else -1
        steps_abs = abs(steps)

        base_delay = self._calculate_delay(speed)
        print(f"Задержка на шаг: {base_delay:.4f} сек")

        start_time = time.time()
        last_progress_time = start_time

        for i in range(steps_abs):
            self.perform_step(direction)
            time.sleep(base_delay)

            current_time = time.time()
            if current_time - last_progress_time >= PROGRESS_OUTPUT_TIMEOUT:
                self._print_progress(i, steps_abs, start_time)
                last_progress_time = current_time

        if steps_abs > 0:
            self._print_progress(steps_abs, steps_abs, start_time)

    def _print_progress(self, current_step, total_steps, start_time):
        """Вывод прогресса выполнения"""
        if total_steps == 0:
            return

        progress_percent = (current_step / total_steps) * 100
        elapsed_time = time.time() - start_time

        if current_step > 0:
            steps_per_second = current_step / elapsed_time
            remaining_time = (total_steps - current_step) / steps_per_second
            time_info = f", осталось: {remaining_time:.1f} сек"
        else:
            time_info = ""

        print(f"Выполнено: {progress_percent:.1f}% ({current_step}/{total_steps} шагов{time_info})")

    def release(self):
        """Освобождение ресурсов"""
        self.deactivate()
        print("Контроллер отключен")