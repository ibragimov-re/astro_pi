from src.mouth.mouth import Mouth
from src.nexstar.constants import Model
from src.mouth.tracking_mode import TrackingMode

MOUTH_LIST = {
    Model.CGE: Mouth(
        model=Model.CGE,
        has_gps=True,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Celestron Montatura CGX GoTo"),
    Model.SE_4_5: Mouth(
        model=Model.SE_4_5,
        has_gps=True,
        tracking_mode=TrackingMode.ALT_AZ,
        name="Celestron SE 5"),
    "AstroPi": Mouth(
        model=Model.CGE,
        has_gps=False,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Astro Pi Equatorial mount")
}
