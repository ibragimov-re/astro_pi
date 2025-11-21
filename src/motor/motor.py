#!/usr/bin/env python3


class Motor:
    """Параметры шагового двигателя"""

    def __init__(self, name, speed_variation_ratio, rotor_steps, rated_voltage, phase_resistance, max_speed):
        self.name = name
        """Коэффициент редукции"""
        self.speed_variation_ratio = speed_variation_ratio
        """Шаги на оборот ротора (без редуктора)"""
        self.rotor_steps = rotor_steps
        """Номинальное напряжение (Вольт)"""
        self.rated_voltage = rated_voltage
        """Сопротивление обмотки (Ом)"""
        self.phase_resistance = phase_resistance
        """Максимальная скорость"""
        self.max_speed = max_speed

    @property
    def steps_per_turn(self):
        """Полное количество шагов на оборот с учетом редукции"""
        return self.rotor_steps / self.speed_variation_ratio

    def steps_for_degrees(self, degrees):
        """Рассчитать количество шагов для поворота на заданные градусы"""
        return int((degrees / 360.0) * self.steps_per_turn)

    def degrees_for_steps(self, steps):
        """Рассчитать угол поворота для заданного количества шагов"""
        return (steps / self.steps_per_turn) * 360.0