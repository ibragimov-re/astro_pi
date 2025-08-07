

class Coordinate:
    def __init__(self, deg=0, min=0, sec=0):
        self.deg = deg
        self.min = min
        self.sec = sec
    def __str__(self):
        return f"{self.deg}°{self.min}’{self.sec}”"


class Location:
    def __init__(self, lat: Coordinate = Coordinate(), long: Coordinate = Coordinate(), north_south=0, east_west=0):
        self.lat = lat
        self.long = long
        self.north_south = north_south # 0=N, 1=S
        self.east_west = east_west # 0=E, 1=W
    north_south = 0

    def __str__(self):
        direction = "N" if self.north_south == 0 else "S"
        return f"{self.long} W, {self.lat} {direction}"
