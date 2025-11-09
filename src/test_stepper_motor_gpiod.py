#!/usr/bin/env python3
import time
import gpiod

CHIP = 'gpiochip0'
IN1_PIN = 118  # GPIO17 (физический пин 11)
IN2_PIN = 114  # GPIO27 (физический пин 13)
IN3_PIN = 111  # GPIO22 (физический пин 15)
IN4_PIN = 112  # GPIO23 (физический пин 16)

# Последовательность шагов
STEP_SEQUENCE = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
]


class StepperMotor:
    def __init__(self, chip, pins):
        self.chip = gpiod.Chip(chip)
        self.lines = self.chip.get_lines(pins)

        config = gpiod.line_request()
        config.consumer = "stepper-motor"
        config.request_type = gpiod.line_request.DIRECTION_OUTPUT

        self.lines.request(config, defaults=[0, 0, 0, 0])
        self.step_sequence = STEP_SEQUENCE
        self.step_count = len(self.step_sequence)
        self.current_step = 0

    def set_step(self, step_pattern):
        """Устанавливает состояние на выходах"""
        self.lines.set_values(step_pattern)

    def step(self, direction, delay=0.01):
        """Выполняет один шаг в указанном направлении"""
        self.current_step = (self.current_step + direction) % self.step_count
        self.set_step(self.step_sequence[self.current_step])
        time.sleep(delay)

    def rotate(self, steps, delay=0.01):
        """Вращает двигатель на указанное количество шагов"""
        direction = 1 if steps > 0 else -1
        for _ in range(abs(steps)):
            self.step(direction, delay)

    def stop(self):
        """Останавливает двигатель (отключает все катушки)"""
        self.set_step([0, 0, 0, 0])

    def __del__(self):
        """Освобождаем ресурсы при удалении объекта"""
        self.stop()
        self.lines.release()
        self.chip.close()


# for test
if __name__ == "__main__":
    motor = StepperMotor(CHIP, [IN1_PIN, IN2_PIN, IN3_PIN, IN4_PIN])

    try:
        steps = 64
        print(f"Двигатель вращается по часовой стрелке ({steps} шага)")
        motor.rotate(steps, delay=0.005)

        time.sleep(1)

        print(f"Двигатель вращается против часовой стрелки ({steps} шага)")
        motor.rotate(-steps, delay=0.005)

        print("Тест завершен")

    except KeyboardInterrupt:
        print("\nОстановка по Ctrl+C")
    finally:
        motor.stop()
        print("Двигатель остановлен")