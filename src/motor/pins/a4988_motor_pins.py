from motor.pins.motor_pins import MotorPins


class A4988MotorPins(MotorPins):
    def __init__(self, step: str, dir: str, enable: str = None, ms: list = None):
        super().__init__('A4988')
        self.step = step
        self.dir = dir
        self.enable = enable
        self.ms = ms