import smbus
import time
import math

# MPU6050 registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# I2C bus (I2C6, GPIO 22/23 on Raspberry Pi)
print("Opening I2C bus 6...")
try:
    bus = smbus.SMBus(6)
    print("I2C bus 6 opened successfully.")
except Exception as e:
    print(f"Failed to open I2C bus 6: {e}")
    raise

def mpu6050_init():
    print("Attempting to initialize MPU6050 at address 0x68...")
    time.sleep(1)  # Delay to let the bus settle
    retries = 3
    for attempt in range(retries):
        try:
            bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
            print("MPU6050 woken up successfully.")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt == retries - 1:
                print(f"Failed to wake up MPU6050 after {retries} attempts.")
                raise
            time.sleep(0.5)
    time.sleep(0.1)

def read_word(reg):
    retries = 3
    for attempt in range(retries):
        try:
            high = bus.read_byte_data(MPU6050_ADDR, reg)
            low = bus.read_byte_data(MPU6050_ADDR, reg + 1)
            value = (high << 8) + low
            if value >= 0x8000:
                return -((65535 - value) + 1)
            return value
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} to read register {reg} failed: {e}")
            if attempt == retries - 1:
                print(f"Failed to read word from register {reg} after {retries} attempts.")
                raise
            time.sleep(0.1)
    return value

def get_acceleration():
    accel_x = read_word(ACCEL_XOUT_H) / 16384.0  # Scale factor for ±2g
    accel_y = read_word(ACCEL_XOUT_H + 2) / 16384.0
    accel_z = read_word(ACCEL_XOUT_H + 4) / 16384.0
    return accel_x, accel_y, accel_z

def get_gyro_data():
    gyro_x = read_word(GYRO_XOUT_H) / 131.0  # Scale factor for ±250°/s
    gyro_y = read_word(GYRO_XOUT_H + 2) / 131.0
    gyro_z = read_word(GYRO_XOUT_H + 4) / 131.0
    return gyro_x, gyro_y, gyro_z

def calculate_angles(accel_x, accel_y, accel_z):
    pitch = math.atan2(accel_y, math.sqrt(accel_x * accel_x + accel_z * accel_z)) * 180 / math.pi
    roll = math.atan2(-accel_x, accel_z) * 180 / math.pi
    return pitch, roll

def mpu6050_close():
    print("Closing I2C bus...")
    try:
        bus.close()
        print("I2C bus closed successfully.")
    except Exception as e:
        print(f"Failed to close I2C bus: {e}")

if __name__ == "__main__":
    try:
        mpu6050_init()
        print("Reading accelerometer and gyroscope data...")
        for _ in range(5):
            accel_x, accel_y, accel_z = get_acceleration()
            pitch, roll = calculate_angles(accel_x, accel_y, accel_z)
            gyro_x, gyro_y, gyro_z = get_gyro_data()
            print(f"Accelerometer: X={accel_x:.3f}g, Y={accel_y:.3f}g, Z={accel_z:.3f}g")
            print(f"Angles: Pitch={pitch:.2f}°, Roll={roll:.2f}°")
            print(f"Gyroscope: X={gyro_x:.2f}°/s, Y={gyro_y:.2f}°/s, Z={gyro_z:.2f}°/s")
            time.sleep(1)
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        mpu6050_close()
