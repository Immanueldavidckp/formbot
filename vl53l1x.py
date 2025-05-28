import time
import board
import adafruit_vl53l1x

vl53 = None

def vl53l1x_init():
    global vl53
    try:
        i2c = board.I2C()
        vl53 = adafruit_vl53l1x.VL53L1X(i2c, address=0x29)
        print("I2C bus initialized on I2C1 (GPIO 2/3).")
        vl53.distance_mode = 1  # Short range
        print("Distance mode set to short range.")
        vl53.timing_budget = 100
        print("Timing budget set to 100 ms.")
        vl53.start_ranging()
        print("Started ranging...")
        return True
    except Exception as e:
        print(f"Failed to initialize VL53L1X: {e}")
        vl53 = None
        return False

def read_distance(sensor):
    if sensor is None:
        return None
    try:
        if not sensor.data_ready:
            return None
        distance = sensor.distance
        time.sleep(0.1)  # Respect the timing budget
        sensor.clear_interrupt()
        if distance is None or distance <= 0:
            raise ValueError("Invalid distance reading from VL53L1X")
        return distance * 10  # Convert cm to mm
    except Exception as e:
        print(f"VL53L1X read error: {e}")
        try:
            sensor.stop_ranging()
            i2c = board.I2C()
            global vl53
            vl53 = adafruit_vl53l1x.VL53L1X(i2c, address=0x29)
            vl53.distance_mode = 1
            vl53.timing_budget = 100
            vl53.start_ranging()
            print("VL53L1X reinitialized after error.")
            return read_distance(vl53)
        except Exception as reinitialize_error:
            print(f"Failed to reinitialize VL53L1X: {reinitialize_error}")
            return None

def vl53l1x_stop(sensor):
    if sensor is not None:
        try:
            sensor.stop_ranging()
            print("VL53L1X ranging stopped and I2C bus deinitialized.")
        except Exception as e:
            print(f"Error stopping VL53L1X: {e}")
