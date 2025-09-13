#!/usr/bin/env python3

import OPi.GPIO as GPIO
import time

PIN_IN4 = "PD16"
PIN_IN3 = "PD15"
PIN_IN2 = "PD18"
PIN_IN1 = "PD22"

# Константы для двигателя 28BYJ-48
STEPS_PER_REVOLUTION = 4096  # Полный оборот (360°)


class MotorController:
    def __init__(self, in1, in2, in3, in4):
        self.pins = [in1, in2, in3, in4]
        self.is_active = False
        self.current_sequence = 'half'  # По умолчанию полушаговый режим

        # Настройка GPIO
        GPIO.setmode(GPIO.SUNXI)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Последовательности шагов с РАЗНЫМИ задержками
        self.sequences = {
            'full': {
                'steps': [
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1]
                ],
                'min_delay': 0.005,  # МИНИМАЛЬНАЯ задержка для full режима
                'max_delay': 0.02  # МАКСИМАЛЬНАЯ задержка для full режима
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
                'min_delay': 0.001,  # Меньшая задержка для half режима
                'max_delay': 0.01  # Меньшая максимальная задержка
            }
        }

        self.current_step = 0
        self.set_sequence('half')  # Начинаем с полушагового режима

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

        steps = int((degrees / 360.0) * STEPS_PER_REVOLUTION)

        direction = "по часовой" if steps >= 0 else "против часовой"
        print(f"Поворот на {degrees}° ({abs(steps)} шагов, {direction})")
        print(f"Режим: {self.current_sequence}, Скорость: {speed}")

        self.move(steps, speed=speed)
        self.deactivate()

    def move(self, steps, speed=5):
        """
        Движение на указанное количество шагов
        speed: 1-10 (1 - медленно, 10 - быстро)
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

        for i in range(steps_abs):
            self.current_step = (self.current_step + direction) % self.step_count
            self._set_pins(self.sequence[self.current_step])
            time.sleep(base_delay)

            # Прогресс для длинных движений
            if steps_abs > 100 and i % (steps_abs // 10) == 0:
                progress = (i / steps_abs) * 100
                print(f"Выполнено: {progress:.1f}%")

    def _set_pins(self, values):
        """Установка состояний пинов"""
        for pin, value in zip(self.pins, values):
            GPIO.output(pin, value)

    def release(self):
        """Полное отключение"""
        self.deactivate()
        GPIO.cleanup()
        print("Двигатель полностью отключен")


# Интерактивный режим с выбором режима работы
def interactive_mode():
    """Режим интерактивного управления"""
    motor = MotorController(in1=PIN_IN1, in2=PIN_IN2, in3=PIN_IN3, in4=PIN_IN4)

    try:
        print("=== ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ ===")
        print("Доступные режимы:")
        print("  full - полношаговый (больше момент, медленнее)")
        print("  half - полушаговый (плавнее, быстрее)")

        # Выбор режима
        while True:
            mode = input("Выберите режим (full/half, по умолчанию half): ").lower().strip()
            if not mode:
                mode = 'half'
                break
            elif mode in ['full', 'half']:
                break
            else:
                print("Неверный режим! Выберите 'full' или 'half'")

        motor.set_sequence(mode)

        while True:
            try:
                angle_input = input("\nВведите угол (°) или 'q' для выхода: ")
                if angle_input.lower() == 'q':
                    break

                angle = float(angle_input)

                # Для full режима ограничиваем максимальную скорость
                if mode == 'full':
                    speed_input = input("Скорость (1-5, по умолчанию 3): ")
                    max_speed = 5
                else:
                    speed_input = input("Скорость (1-10, по умолчанию 5): ")
                    max_speed = 10

                speed = int(speed_input) if speed_input.strip() else (3 if mode == 'full' else 5)
                speed = max(1, min(max_speed, speed))

                motor.move_degrees(angle, speed=speed)

            except ValueError:
                print("Ошибка ввода! Попробуйте снова.")
            except KeyboardInterrupt:
                break

    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        motor.release()


# Тестовый режим
def test_modes():
    """Тестирование обоих режимов"""
    motor = MotorController(in1=PIN_IN1, in2=PIN_IN2, in3=PIN_IN3, in4=PIN_IN4)

    try:
        print("=== ТЕСТ РЕЖИМОВ ===")

        # Тест полношагового режима (МЕДЛЕННЕЕ)
        print("\n1. Тест FULL режима (скорость 3)")
        motor.set_sequence('full')
        motor.move_degrees(90, speed=3)  # Медленная скорость для full

        time.sleep(1)

        # Тест полушагового режима (можно быстрее)
        print("\n2. Тест HALF режима (скорость 5)")
        motor.set_sequence('half')
        motor.move_degrees(-90, speed=5)  # Быстрее для half

        print("\nТест завершен!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        motor.release()


if __name__ == "__main__":
    print("Выберите тест:")
    print("1 - Интерактивный режим с выбором режима")
    print("2 - Тест обоих режимов")

    try:
        choice = input("Ваш выбор (1/2): ").strip()

        if choice == "1":
            interactive_mode()
        elif choice == "2":
            test_modes()
        else:
            print("Запуск теста режимов по умолчанию")
            test_modes()

    except KeyboardInterrupt:
        print("\nПрервано пользователем")