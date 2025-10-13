#!/usr/bin/env python3

import OPi.GPIO as GPIO
import time
from uln2003_motor_controller import ULN2003Controller
from motor_list import MOTORS

PIN_IN4 = "PD16"
PIN_IN3 = "PD15"
PIN_IN2 = "PD18"
PIN_IN1 = "PD22"

CURRENT_MOTOR = MOTORS.get('28BYJ-48')


def interactive_mode():
    """Режим интерактивного управления"""
    motor = ULN2003Controller(CURRENT_MOTOR, PIN_IN1, PIN_IN2, PIN_IN3, PIN_IN4)

    try:
        print("=== ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ ===")
        print("Доступные режимы:")
        print("  wave - полношаговый, 4-ступенчатая последовательность (32 шага на оборот) - меньший момент, только одна катушка за раз, меньший потребляемый ток")
        print("  full - полношаговый, 4-ступенчатая последовательность (32 шага на оборот) - больше момент, медленнее")
        print("  half - полушаговый, 8-ступенчатая последовательность (64 шага на оборот) - плавнее, быстрее")

        # Выбор режима
        while True:
            mode = input("Выберите режим (wave/full/half, по умолчанию half): ").lower().strip()
            if not mode:
                mode = 'half'
                break
            elif mode in ['wave', 'full', 'half']:
                break
            else:
                print("Неверный режим! Выберите 'wave', 'full' или 'half'")

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
        GPIO.cleanup()


def test_modes():
    """Тестирование обоих режимов"""
    motor = ULN2003Controller(CURRENT_MOTOR, PIN_IN1, PIN_IN2, PIN_IN3, PIN_IN4)

    try:
        print("=== ТЕСТ РЕЖИМОВ ===")

        print("\n1. Тест FULL режима (скорость 3)")
        motor.set_sequence('full')
        motor.move_degrees(60, speed=3)  # Медленная скорость для full

        time.sleep(1)

        print("\n2. Тест WAVE режима (скорость 3)")
        motor.set_sequence('wave')
        motor.move_degrees(-60, speed=3)  # Медленная скорость для wave

        time.sleep(1)

        print("\n3. Тест HALF режима (скорость 8)")
        motor.set_sequence('half')
        motor.move_degrees(60, speed=8)  # Быстрее для half

        print("\nТест завершен!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        motor.release()


if __name__ == "__main__":
    print("Выберите тест:")
    print("1 - Интерактивное управление с выбором режима")
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
