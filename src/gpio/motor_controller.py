#!/usr/bin/env python3
import OPi.GPIO as GPIO
import time

PIN_IN4 = "PD16"
PIN_IN3 = "PD15"
PIN_IN2 = "PD18"
PIN_IN1 = "PD22"

# Константы для двигателя 28BYJ-48
STEPS_PER_REVOLUTION = 4096  # Полный оборот (360°)
STEPS_PER_90_DEGREES = 1024  # Поворот на 90°


class MotorController:
    def __init__(self, in1, in2, in3, in4):
        self.pins = [in1, in2, in3, in4]

        # Настройка пинов, задаем архитектурным именем (строка)
        GPIO.setmode(GPIO.SUNXI)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Последовательности шагов
        self.sequences = {
            'full': [
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ],
            'half': [
                [1, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [1, 0, 0, 1]
            ]
        }

        self.current_step = 0
        self.set_sequence('half')  # Полушаговый режим для плавности

    def set_sequence(self, seq_type='full'):
        """Выбор режима работы: 'full' или 'half'"""
        self.sequence = self.sequences[seq_type]
        self.step_count = len(self.sequence)
        print(f"Установлен режим: {seq_type} ({self.step_count} шагов на цикл)")

    def move_degrees(self, degrees, speed=5, clockwise=True):
        """
        Поворот на заданное количество градусов
        degrees: угол в градусах (положительные - по часовой, отрицательные - против)
        speed: скорость (1-10)
        """
        steps = int((degrees / 360.0) * STEPS_PER_REVOLUTION)
        if not clockwise:
            steps = -steps

        print(f"Поворот на {degrees}° ({steps} шагов)")
        self.move(steps, speed=speed, delay=0.003)

    def move(self, steps, speed=5, delay=0.003):
        """
        Движение на указанное количество шагов
        steps: количество шагов (+ вперед, - назад)
        speed: скорость (1-10)
        delay: базовая задержка
        """
        direction = 1 if steps > 0 else -1
        steps = abs(steps)

        actual_delay = delay / speed

        print(f"Движение: {steps} шагов, скорость: {speed}")

        for i in range(steps):
            self.current_step = (self.current_step + direction) % self.step_count
            self._set_pins(self.sequence[self.current_step])
            time.sleep(actual_delay)

            # Прогресс каждые 10%
            if steps > 100 and i % (steps // 10) == 0:
                progress = (i / steps) * 100
                print(f"Выполнено: {progress:.1f}%")
        # print(f"Выполнено: {100:.1f}%")

    def _set_pins(self, values):
        """Установка состояний пинов"""
        for pin, value in zip(self.pins, values):
            GPIO.output(pin, value)

    def release(self):
        """Отключение двигателя"""
        self._set_pins([0, 0, 0, 0])
        GPIO.cleanup()
        print("Двигатель отключен")


# for test
if __name__ == "__main__":

    motor = MotorController(in1=PIN_IN1, in2=PIN_IN2, in3=PIN_IN3, in4=PIN_IN4)

    try:
        # Для двигателя 28BYJ-48:
        # 360 градусов (1 оборот) = 64 шага, по 5.625 градусов за шаг
        # в двигателе есть редуктор 64:1 => 64 * 64 = 4096 шагов на 1 оборот
        # 90 градусов = 4096 / 4 = 1024
        print("1. Поворот на 90 градусов по часовой стрелке")
        motor.move_degrees(-90, speed=3, clockwise=True)
        time.sleep(1)

        print("\n2. Поворот на 90° против часовой стрелки")
        motor.move_degrees(90, speed=3, clockwise=False)
        time.sleep(1)

        # Поворот на 45°
        print("\n3. Поворот на 45°")
        motor.move_degrees(45, speed=4, clockwise=True)
        time.sleep(1)

        print("\nВсе операции завершены успешно!")

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        motor.release()
