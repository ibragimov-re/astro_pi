#!/bin/bash

python -m src.main -r nexstar

# аргументы сервера Astro pi:
# -t (--type)     выбор типа контроллера двигателей (real - реальный "OPi.GPIO" (по умолчанию), sim - симуляция (kopis "Kompas-3D"))
# -r (--protocol) выбор протокола передачи координат (lx200, nexstar, etc)
# -i (--ip)       адрес хоста сервера
# -p (--port)     порт хоста сервера
# -s (--sync)     включить синхронный режим