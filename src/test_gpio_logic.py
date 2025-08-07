import OPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.SUNXI)  # Логическая нумерация
pin = "PD22"              # Логическое имя
GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()