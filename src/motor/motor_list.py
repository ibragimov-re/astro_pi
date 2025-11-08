from src.motor.motor import Motor

MOTORS = {
    '28BYJ-48': Motor(
        name="28BYJ-48",
        speed_variation_ratio=1 / 63.68395,
        rotor_steps=64,  # 5.625 градуса на шаг (~0,088 c редуктором)
        rated_voltage=5.0,
        phase_resistance=50.0,
        max_speed=1000
    ),
    'NEMA17': Motor(
        name="Nema 17 17HS8401",
        speed_variation_ratio=1.0,  # Без редуктора
        rotor_steps=200,  # 1.8 градуса на шаг
        rated_voltage=12.0,
        phase_resistance=2.8,
        max_speed=200
    )
}