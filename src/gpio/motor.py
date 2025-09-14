class Motor:
    """Параметры шагового двигателя"""

    def __init__(self, name, speed_variation_ratio, rotor_steps, rated_voltage, phase_resistance):
        self.name = name
        """Коэффициент редукции"""
        self.speed_variation_ratio = speed_variation_ratio
        """Шаги на оборот ротора (без редуктора)"""
        self.rotor_steps = rotor_steps
        """Номинальное напряжение (Вольт)"""
        self.rated_voltage = rated_voltage
        """Сопротивление обмотки (Ом)"""
        self.phase_resistance = phase_resistance

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


MOTORS = {
    '28BYJ-48': Motor(
        name="28BYJ-48",
        speed_variation_ratio=1 / 63.68395,
        rotor_steps=64,  # 5.625 градуса на шаг (~0,088 c редуктором)
        rated_voltage=5.0,
        phase_resistance=50.0
    ),
    'NEMA17': Motor(
        name="Nema 17 17HS8401",
        speed_variation_ratio=1.0,  # Без редуктора
        rotor_steps=200,  # 1.8 градуса на шаг
        rated_voltage=12.0,
        phase_resistance=2.8
    )
}
