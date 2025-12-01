import socket
import time
from abc import ABC, abstractmethod

from src.motor.motor_list import MOTORS
from src.mount.controller.mount_real_controller import MountRealController
from src.mount.controller.mount_sim_controller import MountSimController
from src.mount.mount_list import MOUNT_LIST
from src.utils import astropi_utils
from src.utils.app_logger import AppLogger
from src.utils.location import Location, SkyCoordinate

TEST_LOCATION = Location.fromLatLong(58, 0, 54, 56, 16, 28)

DEFAULT_MOUNT = MOUNT_LIST['AstroPi']
CURRENT_MOTOR = MOTORS.get('NEMA17')

POLAR_RA_DEC = SkyCoordinate(38.34401535, 89.26740197)  # Polar Star RA/DEC
ZERO = SkyCoordinate(0.0, 0.0)
RA_0_DEC_90 = SkyCoordinate(0.0, 90.0)
DEFAULT_TARGET = RA_0_DEC_90

class Server(ABC):
    buffer = 1024
    name = 'AstroPi'
    no_logging_commands = [b'e']

    LOG_RAW_COMMANDS = False

    def __init__(self, host='0.0.0.0', port=10001, name='AstroPi', mount_type='real', protocol='', sync=False):
        self.host = host
        self.port = port
        self.name = name
        self.running = False
        self.server_socket = None
        self.logger = AppLogger.info(self.name)
        self._setup_server_socket()
        self.location = TEST_LOCATION  # Location.zero_north_east()
        self.has_gps = False

        self.alignment_completed = True

        self.last_update_time = time.time()
        self.mount_type = mount_type
        self.protocol = protocol
        self.sync = sync

        if mount_type == "sim":
            self.mount = MountSimController(DEFAULT_MOUNT, CURRENT_MOTOR)
        else:
            self.mount = MountRealController(DEFAULT_MOUNT, CURRENT_MOTOR, "MotorX", "MotorY")

        self.tracking_mode = self.mount.params.tracking_mode

        self.mount.set_location(TEST_LOCATION)
        self.mount.set_sync(DEFAULT_TARGET)

    def _setup_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.settimeout(1)  # graceful shutdown timeout

    @abstractmethod
    def handle_command(self, cmd):
        """Abstract method for handle of protocol-specific commands"""
        pass

    def _handle_client(self, conn, addr):
        try:
            self.logger.info(f"Клиент подключен: {addr}")
            while self.running:
                data = None
                try:
                    data = conn.recv(self.get_buffer())
                    if not data:
                        break

                    if self.LOG_RAW_COMMANDS:
                        self.logger.info(f"Получена команда: {data}")

                    response = self.handle_command(data)
                    if response:
                        conn.sendall(response)

                    if self.LOG_RAW_COMMANDS:
                        self.logger.info(f"Отправлен ответ: {response}")

                except (ConnectionResetError, socket.timeout):
                    self.logger.error(f"Соединение разорвано по таймауту: {socket.timeout}")
                    break
                except UnicodeDecodeError as e:
                    self.logger.error(f"Неудалось разобрать команду: {data} (Ошибка: {e})")
                except Exception as e:
                    self.logger.error(f"Ошибка получения команды {data}: {e})")

        finally:
            conn.close()
            self.logger.info(f"Соединение с {addr} закрыто")

    def get_buffer(self):
        return self.buffer

    def get_tracking_mode(self):
        return self.tracking_mode

    def has_gps(self):
        return self.mount.params.has_gps

    def get_location(self):
        return self.location

    def set_location(self, loc: Location):
        self.location = loc

    def cancel_goto(self):
        self.mount.goto_in_progress = False

    def get_sync(self) -> SkyCoordinate:
        return self.mount.sync

    def get_current(self) -> SkyCoordinate:
        return self.mount.current

    def start(self):
        self.running = True
        self.server_socket.listen()
        host_ip = astropi_utils.get_local_ip()
        self.logger.info(f"Сервер {self.name} запущен на {host_ip}:{self.port} (протокол: {self.protocol}, режим: {'синхронный' if self.sync else 'асинхронный'})")

        try:
            while self.running:
                try:
                    conn, addr = self.server_socket.accept()
                    if self.sync:
                        self._handle_client(conn, addr)
                    else:
                        import threading
                        client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr),
                        daemon=True)
                        client_thread.start()
                except socket.timeout:
                    continue
        except Exception as e:
            self.logger.error(f"Ошибка сервера: {e}")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.logger.warning(f"Сервер {self.name} остановлен")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
