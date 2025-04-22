import serial
import re

class GPSSensor:
    def __init__(self, port="/dev/ttyAMA4", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None

    def initialize(self):
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            return True
        except Exception as e:
            print(f"GPS Error: {e}")
            return False

    def read_data(self):
        if not self.serial:
            return None
            
        try:
            line = self.serial.readline().decode('ascii', errors='ignore').strip()
            if line.startswith('$GPRMC'):
                parts = line.split(',')
                if len(parts) > 9 and parts[2] == 'A':
                    return {
                        'time': parts[1][:6],
                        'latitude': self._convert_coord(parts[3], parts[4]),
                        'longitude': self._convert_coord(parts[5], parts[6]),
                        'speed': parts[7],
                        'date': parts[9][:6]
                    }
        except:
            return None

    def _convert_coord(self, coord, direction):
        try:
            deg = float(coord[:2]) if direction in ['N', 'S'] else float(coord[:3])
            minutes = float(coord[2:] if direction in ['N', 'S'] else coord[3:])
            return round(deg + (minutes / 60), 6) * (-1 if direction in ['S', 'W'] else 1)
        except:
            return 0.0

    def close(self):
        if self.serial:
            self.serial.close()
