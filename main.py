import argparse

from src.lx200.lx200_server import ServerLX200
from src.nexstar.nexstar_server import ServerNexStar


def main():
    parser = argparse.ArgumentParser(description='Запуск сервера телескопа')
    parser.add_argument('-p', '--protocol', default='lx200',
                        choices=['lx200', 'nexstar'],
                        help='Протокол сервера (по умолчанию: lx200')
    parser.add_argument('--port', type=int, default=4030,
                        help='Порт сервера (по умолчанию: 4030)')

    args = parser.parse_args()
    server = None
    if args.protocol == 'lx200':
        print(f"Запуск LX200 сервера на порту {args.port}")
        server = ServerLX200()
    elif args.protocol == 'nexstar':
        print(f"Запуск NexStar сервера на порту {args.port}")
        server = ServerNexStar()

    try:
        server.start()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
