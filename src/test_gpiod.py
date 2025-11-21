import time
import gpiod

from gpiod.line import Direction, Value

# gpioinfo gpiochip0 - проверка пинов
#
# На схеме платы пины как правило обозначены именем PXY, где X - буква, а Y цифра.
# В командах управления состоянием motor используется номер линии.
# Номер линии из имени пина получается по формуле: (позиция буквы в алфавите - 1) x32 + номер пина.
# Например PD22 будет (4 - 1) x 32 + 22 = 96 + 22 = 118.
#
# Так же линию можно найти в pins.txt ($ motor readall) или pins.png

LINE = 118  # PD22

with gpiod.request_lines(
    "/dev/gpiochip1",
    consumer="blink-example",
    config={
        LINE: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.ACTIVE
        )
    },
) as request:
    while True:
        request.set_value(LINE, Value.ACTIVE)
        time.sleep(1)
        request.set_value(LINE, Value.INACTIVE)
        time.sleep(1)