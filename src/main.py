import argparse

from src.lx200.lx200_server import ServerLX200
from src.nexstar.nexstar_server import ServerNexStar
from src.utils.app_logger import AppLogger

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 4030

log = AppLogger.info("MAIN")

# Ra и Az - это горизонтальная ось (по экватору/горизонту)
# Dec и Alt - это вертикальная ось (от экватора/горизонта)

def main():
    args = _parse_args()

    is_sync = args.sync or args.type == 'sim'
    protocol = args.protocol

    server = None
    try:
        if protocol == 'lx200':
            server = ServerLX200(args.ip, args.port, args.type, is_sync)
        elif protocol == 'nexstar':
            server = ServerNexStar(args.ip, args.port, args.type, is_sync)
        else:
            raise ValueError(f"Неизвестный протокол: {protocol}")

        server.start()

    except KeyboardInterrupt:
        log.warning("Сервер остановлен")
    except Exception as e:
        log.error(f"Ошибка при запуске сервера: {e}")
    finally:
        if server is not None:
            server.stop()

def _parse_args():
    parser = argparse.ArgumentParser(description='Запуск сервера монтировки')

    parser.add_argument('-r', '--protocol', type=str, default='lx200',
                        choices=['lx200', 'nexstar'],
                        help='Протокол сервера (по умолчанию: lx200')

    parser.add_argument('-i', '--ip', type=str, default=DEFAULT_HOST,
                        help=f'Адрес сервера (по умолчанию: {DEFAULT_HOST})')

    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help=f'Порт сервера (по умолчанию: {DEFAULT_PORT})')

    parser.add_argument('-t', '--type', type=str, default='real',
                        choices=['real', 'sim'],
                        help="Тип мотор-контроллера:  для 'real' требуется библиотека OPi.GPIO, 'sim' для симуляции")

    parser.add_argument('-s', '--sync', action=argparse.BooleanOptionalAction, default=False,
                        help="Синхронный режим (по умолчанию: False)")

    return parser.parse_args()


if __name__ == '__main__':
    main()
