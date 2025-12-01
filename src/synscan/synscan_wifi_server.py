import os
import random
import socket
import threading

# Конфигурация
AP_NAME = f"SynScan_WiFi_{random.randint(1000, 9999)}"  # Случайный ID
AP_PASSWORD = "12345678"  # Пароль (минимум 8 символов)
TCP_PORT = 11882  # Порт для команд SynScan


def setup_access_point():
    """Настраивает точку доступа с помощью hostapd и dnsmasq."""
    # Конфиг hostapd
    with open("/tmp/hostapd.conf", "w") as f:
        f.write(f"""
        interface=wlan0
        driver=nl80211
        ssid={AP_NAME}
        hw_mode=g
        channel=6
        macaddr_acl=0
        auth_algs=1
        ignore_broadcast_ssid=0
        wpa=2
        wpa_passphrase={AP_PASSWORD}
        wpa_key_mgmt=WPA-PSK
        wpa_pairwise=TKIP
        rsn_pairwise=CCMP
        """)

    # Конфиг dnsmasq
    with open("/tmp/dnsmasq.conf", "w") as f:
        f.write(f"""
        interface=wlan0
        dhcp-range=192.168.4.2,192.168.4.100,255.255.255.0,24h
        dhcp-option=3,192.168.4.1
        server=8.8.8.8
        """)

    # Назначаем IP на интерфейс
    os.system("sudo ifconfig wlan0 192.168.4.1 netmask 255.255.255.0")
    # Запускаем hostapd и dnsmasq в фоне
    os.system("sudo hostapd /tmp/hostapd.conf -B")
    os.system("sudo dnsmasq -C /tmp/dnsmasq.conf")


def handle_client(conn, addr):
    """Обрабатывает подключение клиента (например, SynScan App)."""
    print(f"[+] Подключен клиент: {addr}")
    try:
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break
            print(f"[Получено] {data}")
            if data.startswith("K"):
                ra = data[1]
                print(f"Han RA: {ra}")
                conn.send(b"1#")  # Ответ "успех"
            elif data.startswith(":Sd"):
                dec = data[3:].split("#")[0]
                print(f"Установка DEC: {dec}")
                conn.send(b"1#")
            elif data == ":GEP#":
                conn.send(b"03:14:15#+45*30#")  # Пример координат
            else:
                conn.send(b"0#")  # Неизвестная команда
    finally:
        conn.close()
        print(f"[-] Клиент отключен: {addr}")


def start_tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", TCP_PORT))
        s.listen(5)
        print(f"[*] Сервер SynScan запущен на порту {TCP_PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    print(f"[*] Создаю точку доступа: {AP_NAME} (Пароль: {AP_PASSWORD})")
    setup_access_point()