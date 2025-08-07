import OPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)  # Физические нумерация
led_pin = 7               # Физический пин 7 (PD22)

try:
    GPIO.setup(led_pin, GPIO.OUT)
    while True:
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()