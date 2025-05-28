import serial
import time
import pynmea2

# UART3 configuration (likely /dev/ttyAMA2 on Raspberry Pi)
UART_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600  # Common baud rate for GPS modules like NEO-6M

def gps_init():
    try:
        ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=1)
        print("GPS initialized successfully.")
        return ser
    except Exception as e:
        print(f"Failed to initialize GPS: {e}")
        raise

def read_gps(ser):
    try:
        line = ser.readline().decode('ascii', errors='replace').strip()
        if line.startswith('$GNGGA') or line.startswith('$GPGGA'):
            msg = pynmea2.parse(line)
            if msg.latitude and msg.longitude:
                return {
                    'latitude': msg.latitude,
                    'longitude': msg.longitude,
                    'altitude': msg.altitude if msg.altitude else 'N/A',
                    'satellites': msg.num_sats
                }
        return None
    except Exception as e:
        print(f"Error reading GPS data: {e}")
        return None

def gps_close(ser):
    print("Closing GPS UART port...")
    try:
        ser.close()
        print("GPS UART port closed successfully.")
    except Exception as e:
        print(f"Failed to close GPS UART port: {e}")

if __name__ == "__main__":
    try:
        gps = gps_init()
        print("Reading GPS data (press Ctrl+C to stop)...")
        while True:
            data = read_gps(gps)
            if data:
                print(f"Latitude: {data['latitude']:.6f}, Longitude: {data['longitude']:.6f}, "
                      f"Altitude: {data['altitude']} m, Satellites: {data['satellites']}")
            else:
                print("No valid GPS data received.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nGPS test interrupted.")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        gps_close(gps)
