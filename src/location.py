class Coordinate:
    def __init__(self, deg=0, min=0, sec=0):
        self.deg = deg
        self.min = min
        self.sec = sec

    def __str__(self):
        return f"{self.deg}°{self.min}’{self.sec}”"

    @staticmethod
    def zero():
        return Coordinate(0, 0, 0)


class Location:
    def __init__(self, lat: Coordinate = Coordinate(), long: Coordinate = Coordinate(), north_south=0, east_west=0):
        self.lat = lat
        self.long = long
        self.north_south = north_south  # 0=N, 1=S
        self.east_west = east_west  # 0=E, 1=W

    def __str__(self):
        north_south = "N" if self.north_south == 0 else "S"
        east_west = "E" if self.east_west == 0 else "W"

        return f"{self.long} {east_west}, {self.lat} {north_south}"

    @staticmethod
    def zero_north_east():
        return Location(Coordinate.zero(), Coordinate.zero(), 0, 0)

    @staticmethod
    def fromLatLong(lat_deg=0, lat_min=0, lat_sec=0, long_deg=0, long_min=0, long_sec=0, north_south=0, east_west=0):
        lat = Coordinate(lat_deg, lat_min, lat_sec)
        long = Coordinate(long_deg, long_min, long_sec)
        return Location(lat, long, north_south, east_west)
