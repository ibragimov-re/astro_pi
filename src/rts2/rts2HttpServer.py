from flask import Flask, request, jsonify
import math
import time

app = Flask(__name__)

# Эмулируем данные телескопа
telescope = {
    "id": 1,
    "type": 2,
    "name": "AstroPi",
    "connected": True,
    "readonly": False,
    "slewing": False,
    "tracking": True,
    "ra": 0.0,
    "dec": 0.0,
    "longitude": 0.0,
    "latitude": 0.0,
    "altitude": 0.0,
    "target_distance": 0.0
}


@app.route('/api/devbytype', methods=['GET'])
def get_devices_by_type():
    """Список устройств по типу (тип 2 = телескоп)"""
    dev_type = int(request.args.get('t', 0))
    if dev_type == 2:
        return jsonify([telescope["name"]])
    return jsonify([])


@app.route('/api/deviceinfo', methods=['GET'])
def get_device_info():
    """Информация о телескопе"""
    return jsonify({
        "device": {
            "name": telescope["name"],
            "type": telescope["type"],
            "connected": telescope["connected"]
        },
        "readonly": telescope["readonly"],
        "status": "TRACKING" if telescope["tracking"] else "IDLE"
    })


@app.route('/api/get', methods=['GET'])
def get_device_status():
    """Текущее состояние и координаты"""
    return jsonify({
        "d": {
            "TEL": {
                "ra": telescope["ra"] * 180 / math.pi,  # в градусах
                "dec": telescope["dec"] * 180 / math.pi,
                "slewing": telescope["slewing"]
            },
            "LONGITUD": telescope["longitude"] * 180 / math.pi,
            "LATITUDE": telescope["latitude"] * 180 / math.pi,
            "ALTITUDE": telescope["altitude"],
            "target_distance": telescope["target_distance"] * 180 / math.pi
        }
    })


@app.route('/api/cmd', methods=['GET'])
def handle_command():
    """Обработка команд (GOTO и других)"""
    cmd = request.args.get('c', '')
    if cmd.startswith('move'):
        if telescope["slewing"]:
            print(f"Telescope's steel slewing: RA={telescope['ra']}, Dec={telescope['dec']}")
            jsonify({"ret": -1})
        # Парсим координаты GOTO
        parts = cmd[5:].split(' ')
        if len(parts) == 2:
            telescope["ra"] = float(parts[0]) * math.pi / 180  # в радианы
            telescope["dec"] = float(parts[1]) * math.pi / 180
            telescope["slewing"] = True
            print(f"GOTO command: RA={telescope['ra']}, Dec={telescope['dec']}")

            # Эмулируем движение
            time.sleep(10)
            telescope["slewing"] = False

            print(f"GOTO command complete!: RA={telescope['ra']}, Dec={telescope['dec']}")

            return jsonify({"ret": 0})  # успех

    return jsonify({"ret": -1})  # ошибка


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8889, debug=False)