from src.mount.mount import Mount
from src.mount.tracking_mode import TrackingMode
from src.nexstar.constants import Model

MOUNT_LIST = {
    'Celestron_Montatura_CGX': Mount(
        model=Model.CGE,
        has_gps=True,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Celestron Montatura CGX GoTo"),
    'Celestron_SE_5': Mount(
        model=Model.SE_4_5,
        has_gps=True,
        tracking_mode=TrackingMode.ALT_AZ,
        name="Celestron SE 5"),
    'AstroPi': Mount(
        model=Model.ADVANCED_GT,
        has_gps=False,
        tracking_mode=TrackingMode.EQ_NORTH,
        name="Astro Pi Equatorial mount")
}
