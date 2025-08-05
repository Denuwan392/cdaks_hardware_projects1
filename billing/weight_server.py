from flask import Flask, jsonify
import serial
import threading
import time

from flask_cors import CORS
import serial, threading, time




app = Flask(__name__)
CORS(app)

SERIAL_PORT = '/dev/tty.usbmodem11301'
BAUD_RATE = 57600
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)  # Faster reads

current_weight = 0.0
last_command = ""

def read_serial():
    global current_weight, last_command
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"[Serial] {line}")
                if line.lower() in ["add", "reset", "bill"]:
                    last_command = line.lower()
                else:
                    weight = float(line)/1000  # Convert grams to kg
                    if 0 <= weight <= 1000:
                        current_weight = weight
        except Exception as e:
            print(f"[Serial Read Error] {e}")
        time.sleep(0.05)




    

@app.route('/get-weight')
def get_weight():
    return jsonify({'weight': round(current_weight, 2)})

@app.route('/')
def root():
    return jsonify({'message': 'Go to /get-weight for weight'})


@app.route('/get-command')
def get_command():
    global last_command
    cmd = last_command
    last_command = ""  # Clear after reading
    return jsonify({'command': cmd})


if __name__ == '__main__':
    print("[Flask] Starting weight API on port 5002...")
    threading.Thread(target=read_serial, daemon=True).start()
    app.run(host='0.0.0.0', port=5003)
