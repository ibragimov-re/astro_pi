#!/usr/bin/env python3

import OPi.GPIO as GPIO
import time
from a4988_motor_controller import A4988MotorController
from motor_list import MOTORS

# двигатель 1
PIN_DIR_FIRST = "PD16"     # 18 зеленый
PIN_STEP_FIRST = "PD15"    # 16 синий
PIN_ENABLE_FIRST = "PD18"  # 12 фиолетовый

# двигатель 2
PIN_DIR_SECOND = "PD22"     # 7 зеленый
PIN_STEP_SECOND = "PD25"    # 5 синий
PIN_ENABLE_SECOND = "PD26"  # 3 фиолетовый

# микрошаг
PIN_MS1 = ""
PIN_MS2 = ""
PIN_MS3 = ""


CURRENT_MOTOR = MOTORS.get('NEMA17')


def interactive_mode():
    """Режим интерактивного управления"""
    motor = A4988MotorController(CURRENT_MOTOR, PIN_STEP_FIRST, PIN_DIR_FIRST, PIN_ENABLE_FIRST)
    motor2 = A4988MotorController(CURRENT_MOTOR, PIN_STEP_SECOND, PIN_DIR_SECOND, PIN_ENABLE_SECOND)

    motor.set_microstep(16)
    motor2.set_microstep(16)

    try:
        print("=== ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ ===")

        while True:
            try:
                angle_input = input("\nВведите угол (°) или 'q' для выхода: ")
                if angle_input.lower() == 'q':
                    break

                angle = float(angle_input)

                speed_default = 1
                speed_max = 5
                speed_input = input(f"Скорость (1-{speed_max}), по-умолчанию {speed_default}): ")
                speed = int(speed_input) if speed_input.strip() else speed_default
                speed = max(1, min(speed_max, speed))

                ms_default = 8
                ms_max = 16
                ms_input = input("Выберите микрошаг (1/2/4/8/16, по умолчанию 16): ").strip()
                ms = int(ms_input) if ms_input.strip() else ms_default
                ms = max(1, min(ms_max, ms))
                motor.set_microstep(ms)
                motor2.set_microstep(ms)

                motor.move_degrees(angle, speed)
                motor2.move_degrees(angle, speed)

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
        motor2.release()
        GPIO.cleanup()


def test_modes():
    motor = A4988MotorController(CURRENT_MOTOR, PIN_STEP_FIRST, PIN_DIR_FIRST, PIN_ENABLE_FIRST)
    motor2 = A4988MotorController(CURRENT_MOTOR, PIN_STEP_SECOND, PIN_DIR_SECOND, PIN_ENABLE_SECOND)

    try:
        print("=== ТЕСТ РЕЖИМОВ ===")

        test_angles = [180, -90]
        test_speed = 3

        microsteps_to_test = [1, 2, 4, 8, 16]

        for microstep in microsteps_to_test:
            print(f"\n--- Тест микрошага 1/{microstep} ---")
            motor.set_microstep(microstep)
            motor2.set_microstep(microstep)

            for angle in test_angles:
                reduced_angle = angle / microstep
                print(f"Поворот на {reduced_angle}°")
                motor.move_degrees(reduced_angle, test_speed)
                motor2.move_degrees(reduced_angle, test_speed)

                time.sleep(1)

        print("\nТест завершен!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        motor.release()
        motor2.release()


if __name__ == "__main__":
    GPIO.cleanup()

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
