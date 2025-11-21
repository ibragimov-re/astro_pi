import argparse

from src.lx200.lx200_server import ServerLX200
from src.nexstar.nexstar_server import ServerNexStar
from src.utils.app_logger import AppLogger

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 4030

log = AppLogger.info("MAIN")

def get_motor_controller_type():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=str, choices=['def', 'sim'], default='def',
                        help="Тип мотор-контроллера: 'real' для A4988 (требуется OPi.GPIO), 'sim' для симуляции")
    args = parser.parse_args()
    return args.type

def main():
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

    args = parser.parse_args()

    server = None
    is_sync = args.sync or args.type == 'sim'
    if args.protocol == 'lx200':
        server = ServerLX200(args.ip, args.port, args.type, is_sync)
    elif args.protocol == 'nexstar':
        server = ServerNexStar(args.ip, args.port, args.type, is_sync)

    try:
        server.start()
    except KeyboardInterrupt:
        log.warning("\nСервер остановлен")
    except Exception as e:
        log.error(f"Ошибка при запуске сервера: {e}")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
