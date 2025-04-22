
import time
from i2c_driver import I2CDevice

VL53L0X_ADDR = 0x29

sensor = I2CDevice(1, VL53L0X_ADDR)

def start_ranging():
    sensor.write_byte_data(0x00, 0x01)  # start ranging

def stop_ranging():
    sensor.write_byte_data(0x00, 0x00)  # stop ranging

def get_distance():
    return sensor.read_word_data(0x14)

try:
    print("VL53L0X starting...")
    start_ranging()
    time.sleep(0.2)

    while True:
        dist = get_distance()
        print(f"Distance: {dist} mm")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopping...")
    stop_ranging()
    sensor.close()
