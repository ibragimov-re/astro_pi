#!/bin/bash

python3 -m src.main -r nexstar -t real

# аргументы сервера Astro pi:
# -t выбор типа контроллера двигателей (real - реальный (OPi.GPIO), sim - симуляция (kopis "Kompas-3D"))
# -r выбор протокола передачи координат (lx200, nexstar, etc)
# -i адрес хоста сервера
# -p порт хоста сервера