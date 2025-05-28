import time
import board
import busio
import adafruit_vl53l1x

# Global variables to store the VL53L1X sensor object and I2C bus
vl53 = None
i2c = None

def vl53l1x_init():
    """
    Initialize the VL53L1X sensor on I2C bus 1 with address 0x29.
    Returns:
        bool: True if initialization is successful, False otherwise
    """
    global vl53, i2c
    try:
        # Explicitly initialize the I2C bus with a lock to prevent conflicts
        i2c = busio.I2C(board.SCL, board.SDA, frequency=10000)  # Lower frequency to 10 kHz for stability
        print("I2C bus initialized on I2C1 (GPIO 2/3) with frequency 10 kHz.")
        
        # Initialize the VL53L1X sensor
        vl53 = adafruit_vl53l1x.VL53L1X(i2c, address=0x29)
        print("VL53L1X sensor detected.")

        # Configure the sensor
        vl53.distance_mode = 1  # 1 = Short range (up to 1.3m)
        print("Distance mode set to short range.")
        vl53.timing_budget = 100  # Set timing budget to 100 ms
        print("Timing budget set to 100 ms.")
        vl53.start_ranging()
        print("Started ranging...")
        return True
    except Exception as e:
        print(f"Failed to initialize VL53L1X: {e}")
        vl53 = None
        i2c = None
        return False

def read_distance(sensor):
    """
    Read the distance from the VL53L1X sensor.
    Args:
        sensor: The VL53L1X sensor object
    Returns:
        float: Distance in millimeters, or None if reading fails
    """
    if sensor is None:
        return None
    try:
        if not sensor.data_ready:  # Check if a new measurement is ready
            return None
        distance = sensor.distance  # Distance in centimeters
        sensor.clear_interrupt()  # Clear the interrupt flag for the next measurement
        if distance is None or distance <= 0:  # Check for invalid readings
            raise ValueError("Invalid distance reading from VL53L1X")
        return distance * 10  # Convert centimeters to millimeters
    except Exception as e:
        print(f"VL53L1X read error: {e}")
        # Attempt to reinitialize the sensor on failure
        try:
            sensor.stop_ranging()
            global vl53, i2c
            i2c = busio.I2C(board.SCL, board.SDA, frequency=10000)
            vl53 = adafruit_vl53l1x.VL53L1X(i2c, address=0x29)
            vl53.distance_mode = 1
            vl53.timing_budget = 100
            vl53.start_ranging()
            print("VL53L1X reinitialized after error.")
            return read_distance(vl53)  # Retry reading
        except Exception as reinitialize_error:
            print(f"Failed to reinitialize VL53L1X: {reinitialize_error}")
            return None
    finally:
        time.sleep(0.1)  # Respect the timing budget (100 ms)

def vl53l1x_stop(sensor):
    """
    Stop ranging and clean up the VL53L1X sensor and I2C bus.
    Args:
        sensor: The VL53L1X sensor object
    """
    global i2c
    if sensor is not None:
        try:
            sensor.stop_ranging()
            print("VL53L1X ranging stopped.")
        except Exception as e:
            print(f"Error stopping VL53L1X: {e}")
    if i2c is not None:
        try:
            i2c.deinit()  # Explicitly deinitialize the I2C bus
            print("I2C bus deinitialized.")
        except Exception as e:
            print(f"Error deinitializing I2C bus: {e}")
        finally:
            i2c = None

def main():
    """
    Standalone function to test the VL53L1X sensor.
    Initializes the sensor, reads distances in a loop, and cleans up on exit.
    """
    print("Starting VL53L1X standalone test... (Press Ctrl+C to stop)")
    
    # Initialize the sensor
    if not vl53l1x_init():
        print("Exiting due to sensor initialization failure.")
        return

    try:
        while True:
            distance = read_distance(vl53)
            if distance is not None:
                print(f"Distance: {distance:.1f} mm")
            else:
                print("Distance: N/A (reading failed)")
            time.sleep(0.5)  # Delay to avoid overwhelming the sensor
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        vl53l1x_stop(vl53)
        print("Program terminated.")

if __name__ == "__main__":
    main()
