#!/usr/bin/env python3

import time
from abc import abstractmethod

PROGRESS_OUTPUT_TIMEOUT = 0.5


class BaseMotorController:
    """Базовый класс для всех контроллеров шаговых двигателей"""

    def __init__(self, motor_params):
        self.motor_params = motor_params
        self.is_active = False
        print(f"Инициализирован двигатель: {self.motor_params.name}")
        print(f"Шагов на оборот: {self.motor_params.steps_per_turn:.0f}")

    @abstractmethod
    def activate(self):
        """Активация двигателя (должна быть реализована в потомке)"""
        raise NotImplementedError("Метод activate должен быть реализован в потомке")

    @abstractmethod
    def deactivate(self):
        """Деактивация двигателя (должна быть реализована в потомке)"""
        raise NotImplementedError("Метод deactivate должен быть реализован в потомке")

    @abstractmethod
    def perform_step(self, direction):
        """Выполнение одного шага (должна быть реализована в потомке)"""
        raise NotImplementedError("Метод perform_step должен быть реализован в потомке")

    def move_degrees(self, degrees, speed=5):
        """
        Поворот на заданное количество градусов
        degrees: угол в градусах со знаком
        speed: скорость (1-10)
        """
        self.activate()

        # Используем параметры двигателя для расчета шагов
        steps = self.motor_params.steps_for_degrees(degrees)

        direction_str = "по часовой" if steps >= 0 else "против часовой"
        print(f"Поворот на {degrees}° ({abs(steps)} шагов, {direction_str})")
        print(f"Скорость: {speed}")

        self.move(steps, speed=speed)
        self.deactivate()

    def move(self, steps, speed=5):
        """
        Движение на указанное количество шагов
        steps: количество шагов (+ по часовой, - против часовой)
        speed: скорость (1-10)
        """
        if steps == 0:
            return

        direction = 1 if steps >= 0 else -1
        steps_abs = abs(steps)

        # Расчет задержки (должен быть реализован в потомке)
        base_delay = self._calculate_delay(speed)
        print(f"Задержка на шаг: {base_delay:.4f} сек")

        # Отслеживание прогресса
        start_time = time.time()
        last_progress_time = start_time

        for i in range(steps_abs):
            self.perform_step(direction)
            time.sleep(base_delay)

            # Вывод прогресса по времени
            current_time = time.time()
            if current_time - last_progress_time >= PROGRESS_OUTPUT_TIMEOUT:
                self._print_progress(i, steps_abs, start_time)
                last_progress_time = current_time

        # Финальный прогресс
        if steps_abs > 0:
            self._print_progress(steps_abs, steps_abs, start_time)

    @abstractmethod
    def _calculate_delay(self, speed):
        """Расчет задержки между шагами (должен быть реализован в потомке)"""
        raise NotImplementedError("Метод _calculate_delay должен быть реализован в потомке")

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

    @abstractmethod
    def release(self):
        """Освобождение ресурсов (должен быть реализован в потомке)"""
        raise NotImplementedError("Метод release должен быть реализован в потомке")