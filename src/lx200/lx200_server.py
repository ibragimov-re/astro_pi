from src.server import Server


class ServerLX200(Server):
    buffer = 8

    def __init__(self, host='0.0.0.0', port=4030):
        super().__init__(host, port, Server.name + ' [LX200]')

    def get_buffer(self):
        return self.buffer

    def handshake(self, data):
        self.logger.info(f"Клиент запрашивает состояние. ОК")
        return data[1] + "#"

    def handle_command(self, data):
        try:
            cmd = data.decode('ascii').strip()
            self.logger.debug(f"Получена команда: {cmd}")

            if not cmd:
                return None

            if cmd == ":GR#":
                return b"12:34:56#"
            elif cmd == ":GD#":
                return b"+45*30#"
            elif cmd == ":Q#":
                return b"1"
            elif cmd == ":CM#":
                return b"M31#"
            elif cmd.startswith("#"):
                return self.handshake(cmd).encode('ascii')

        except UnicodeDecodeError:
            hex_cmd = data.hex()
            self.logger.debug(f"Бинарная команда: {hex_cmd}")
            return b"#"

        return None