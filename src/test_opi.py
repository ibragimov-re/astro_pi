import OPi.GPIO as GPIO
import time

# GPIO.setboard(GPIO.OPi3)
# GPIO.setmode(GPIO.BOARD)  # Физические нумерация
# pin = 7               # Физический пин 7 (PD22), 12 (114, PD18)

# GPIO.setmode(GPIO.BCM)
# pin = 118

# GPIO.setmode(GPIO.SOC)
# pin = 118

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