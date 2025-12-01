from src.nexstar.constants import Model
from src.mount.tracking_mode import TrackingMode


class Mount:

    def __init__(self, model: Model, has_gps, tracking_mode: TrackingMode, name="No name mount with GoTo"):
        self.name = name
        self.model = model
        self.has_gps = has_gps
        self.tracking_mode = tracking_mode  # как я понял это определяет какой будет тип компенсации вращения - по экваториальной или азимутальной оси
