import serial
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

latest_weight = 0.0

def read_from_serial(port, baudrate):
    global latest_weight
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"[Serial] Connected to {port} at {baudrate} baud.")
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(f"Raw serial: {line}")
            if line.startswith("weight:"):
                try:
                    latest_weight = float(line.split(":")[1])
                except ValueError:
                    pass
            time.sleep(0.05)  # avoid tight loop
    except Exception as e:
        print(f"[Serial Error] {e}")


@app.route('/weight')
def get_weight():
    return jsonify({'weight': latest_weight})

if __name__ == '__main__':
    serial_port = '/dev/tty.usbmodem1301'  # Update as needed
    baud_rate = 57600

    serial_thread = threading.Thread(target=read_from_serial, args=(serial_port, baud_rate))
    serial_thread.daemon = True  # so it exits when main thread exits
    serial_thread.start()

    print("[Flask] Starting Flask server on port 5002...")
    app.run(port=5002)
