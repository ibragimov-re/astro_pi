import kopis as GPIO
import time


print("================================= Работа с пинами =================================")

print("Установка режима нумерации пинов")
GPIO.setmode(GPIO.BOARD)

print("Установка режимов у пинов")
GPIO.setup(8, GPIO.IN)
GPIO.setup(12,GPIO.OUT)
time.sleep(2)

print("Изменение состояния пина")
GPIO.output(12, GPIO.HIGH)
time.sleep(2)

print("Цикличное изменение состояния пина")
for i in range(0, 10):
    GPIO.setup(8, GPIO.IN)
    time.sleep(0.1)
    GPIO.setup(8, GPIO.OUT)
    time.sleep(0.1)
time.sleep(2)

print("Очистка пина")
GPIO.cleanup(12)
time.sleep(2)

print("Очистка всех пинов")
GPIO.cleanup()
time.sleep(2)


print("================================ Работа с моторами ================================")

horizontal_motor_name = "#Nema17HS8401_Horizontal"
vertical_motor_name = "#Nema17HS8401_Vertical"

print("Перемещение моторов")
print("Поворот по горизонтали на 180° по ч.с.")
GPIO.kopis_motorsim.move_degrees(horizontal_motor_name, 180, 3)
print("Поворот по горизонтали на 90° по п.ч.с.")
GPIO.kopis_motorsim.move_degrees(horizontal_motor_name, -90, 3)
print("Поворот по вертикали на 90° по ч.с.")
GPIO.kopis_motorsim.move_degrees(vertical_motor_name, 90, 1)
print("Поворот по вертикали на 90° по п.ч.с.")
GPIO.kopis_motorsim.move_degrees(vertical_motor_name, -90, 1)
time.sleep(2)

print("Выставление моторов в исходное положение для экваториальной монтировки")
GPIO.kopis_motorsim.setup_motors_by_mount_type(GPIO.kopis_motorsim.EQ)
time.sleep(2)


print("====================== Использование дополнительных функций ======================")

print("Печать таблицы со всей информацией о пинах")
GPIO.kopis_extra.print_board_pins()
time.sleep(2)

print("Запуск заготовленных тестовых управляющих программ, реализованных внутри библиотеки симулятора (в C++ коде)")
GPIO.kopis_extra.test_motors()
GPIO.kopis_extra.test_gpio_pins()