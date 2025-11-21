#!/usr/bin/env python3

import OPi.GPIO as GPIO
import time
import threading

from src.motor.controller.a4988_motor_controller import A4988MotorController
from src.motor.motor_list import MOTORS

# двигатель Ra
PIN_DIR_FIRST = "PD22"     # 7 зеленый
PIN_STEP_FIRST = "PD25"    # 5 синий
PIN_ENABLE_FIRST= "PD26"  # 3 фиолетовый
PIN_MS_ALL_FIRST = "PL2"   # 8 синий

# пины двигателя Dec
PIN_DIR_SECOND = "PD16"      # 18 зеленый
PIN_STEP_SECOND = "PD15"     # 16 синий
PIN_ENABLE_SECOND = "PD18"   # 12 фиолетовый
PIN_MS_ALL_SECOND = "PL3"    # 10 сиреневый

CURRENT_MOTOR = MOTORS.get('NEMA17')


def move_motor_sync(motor, angle, speed):
    """Функция для движения двигателя в отдельном потоке"""
    motor.move_degrees(angle, speed)


def interactive_mode():
    """Режим интерактивного управления"""
    motor = A4988MotorController(CURRENT_MOTOR, PIN_STEP_FIRST, PIN_DIR_FIRST, PIN_ENABLE_FIRST, [PIN_MS_ALL_FIRST, PIN_MS_ALL_FIRST, PIN_MS_ALL_FIRST])
    motor2 = A4988MotorController(CURRENT_MOTOR, PIN_STEP_SECOND, PIN_DIR_SECOND, PIN_ENABLE_SECOND, [PIN_MS_ALL_SECOND, PIN_MS_ALL_SECOND, PIN_MS_ALL_SECOND])

    motor.set_microstep(16)
    motor2.set_microstep(16)

    try:
        print("=== ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ ===")
        print("Двигатели будут запускаться ОДНОВРЕМЕННО")

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

                ms_default = 16
                ms_max = 16
                ms_input = input("Выберите микрошаг (1/2/4/8/16, по умолчанию 16): ").strip()
                ms = int(ms_input) if ms_input.strip() else ms_default
                ms = max(1, min(ms_max, ms))
                motor.set_microstep(ms)
                motor2.set_microstep(ms)

                print(f"Запуск ДВУХ двигателей одновременно: {angle}°, скорость {speed}, микрошаг 1/{ms}")

                # Создаем потоки для каждого двигателя
                thread1 = threading.Thread(target=move_motor_sync, args=(motor, angle, speed))
                thread2 = threading.Thread(target=move_motor_sync, args=(motor2, angle, speed))

                # Запускаем потоки одновременно
                thread1.start()
                thread2.start()

                # Ждем завершения обоих потоков
                thread1.join()
                thread2.join()

                print("Оба двигателя завершили движение")

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
        print("=== ТЕСТ РЕЖИМОВ (ОДНОВРЕМЕННЫЙ) ===")

        test_angles = [180, -90]
        test_speed = 3

        microsteps_to_test = [1, 2, 4, 8, 16]

        for microstep in microsteps_to_test:
            print(f"\n--- Тест микрошага 1/{microstep} ---")
            motor.set_microstep(microstep)
            motor2.set_microstep(microstep)

            for angle in test_angles:
                reduced_angle = angle / microstep
                print(f"ОДНОВРЕМЕННЫЙ поворот на {reduced_angle}°")

                # Создаем и запускаем потоки
                thread1 = threading.Thread(target=move_motor_sync, args=(motor, reduced_angle, test_speed))
                thread2 = threading.Thread(target=move_motor_sync, args=(motor2, reduced_angle, test_speed))

                thread1.start()
                thread2.start()

                # Ждем завершения
                thread1.join()
                thread2.join()

                print("Оба двигателя завершили движение")
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
    print("1 - Интерактивное управление с ОДНОВРЕМЕННЫМ запуском")
    print("2 - Тест обоих режимов с ОДНОВРЕМЕННЫМ запуском")

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