from src.mouth.mouth import Mouth
from src.mouth.tracking_mode import TrackingMode
from src.nexstar.constants import Model

MOUTH_LIST = {
    'Celestron_Montatura_CGX': Mouth(
        model=Model.CGE,
        has_gps=True,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Celestron Montatura CGX GoTo"),
    'Celestron_SE_5': Mouth(
        model=Model.SE_4_5,
        has_gps=True,
        tracking_mode=TrackingMode.ALT_AZ,
        name="Celestron SE 5"),
    'AstroPi': Mouth(
        model=Model.ADVANCED_GT,
        has_gps=False,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Astro Pi Equatorial mount")
}
