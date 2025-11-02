import threading

HIGH_SPEED = 5
MID_SPEED = 3
LOW_SPEED = 1

class MouthEqController:
    curr_ra = 0.0
    curr_dec = 0.0

    def __init__(self, mouth, motor_h_controller, motor_v_controller):
        self.mouth = mouth
        self.motorRa = motor_h_controller
        self.motorDec = motor_v_controller

    def goto(self, ra, dec):
        try:
            print(f"Инициализация поворота: {ra}°, {dec}°")

            # Создаем потоки для каждого двигателя
            thread1 = threading.Thread(target=self.move_motor_sync, args=(self.motorRa, ra, MID_SPEED))
            thread2 = threading.Thread(target=self.move_motor_sync, args=(self.motorDec, dec, MID_SPEED))

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
            print("Прервано пользователем")

        return {self.curr_ra, self.curr_dec}

    def move_motor_sync(self, motor, angle, speed):
        """Функция для движения двигателя в отдельном потоке"""
        motor.move_degrees(angle, speed)
    
