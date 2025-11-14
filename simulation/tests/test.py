import kopis as GPIO
import time

GPIO.setmode(GPIO.SUNXI)

GPIO.setup(8, GPIO.IN)
GPIO.setup(12,GPIO.OUT)


GPIO.output(12, GPIO.HIGH)

for i in range(0,10):
    GPIO.setup(8, GPIO.IN)
    time.sleep(0.1)
    GPIO.setup(8, GPIO.OUT)
    time.sleep(0.1)


GPIO.cleanup(12)
time.sleep(5)
print ("123")
GPIO.cleanup()
time.sleep(10)
