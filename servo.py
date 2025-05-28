import pigpio
import time

# Servo GPIO pins (adjust as needed)
HORIZONTAL_SERVO_PIN = 23  # GPIO 23 for horizontal servo
VERTICAL_SERVO_PIN = 18    # GPIO 18 for vertical servo

# Servo pulse width range (in microseconds)
SERVO_MIN_PULSE = 500   # 0 degrees
SERVO_MAX_PULSE = 2500  # 180 degrees

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise Exception("Failed to connect to pigpiod daemon.")

def angle_to_pulse(angle):
    # Convert angle (0-180) to pulse width (500-2500 us)
    return int(SERVO_MIN_PULSE + (angle / 180.0) * (SERVO_MAX_PULSE - SERVO_MIN_PULSE))

def move_servo(pin, angle, speed=2):
    # Move servo to the target angle smoothly
    current_pulse = pi.get_servo_pulsewidth(pin)
    if current_pulse == 0:
        current_pulse = angle_to_pulse(0)  # Assume starting at 0 if not set
    target_pulse = angle_to_pulse(angle)
    step = 20 if target_pulse > current_pulse else -20  # Increased step size for faster movement
    for pulse in range(current_pulse, target_pulse + step, step):
        pi.set_servo_pulsewidth(pin, pulse)
        time.sleep(0.005 / speed)  # Reduced sleep time for faster movement
    return angle

def servo_init():
    print("Initializing servos...")
    # Set initial positions
    pi.set_servo_pulsewidth(HORIZONTAL_SERVO_PIN, angle_to_pulse(0))
    pi.set_servo_pulsewidth(VERTICAL_SERVO_PIN, angle_to_pulse(0))
    print("Servos initialized at 0 degrees.")

def servo_move(horizontal_angle, vertical_angle, direction):
    """
    Perform one step of servo movement and return the updated angles and direction.
    Returns: (horizontal_angle, vertical_angle, direction, at_extreme)
    """
    # Move horizontal servo
    horizontal_angle += direction * 1
    if horizontal_angle >= 80:
        horizontal_angle = 80
        direction = -1
    elif horizontal_angle <= 0:
        horizontal_angle = 0
        direction = 1
    move_servo(HORIZONTAL_SERVO_PIN, horizontal_angle, speed=3)  # Increased speed

    # Check if at horizontal extreme (0° or 80°)
    at_extreme = (horizontal_angle == 0 or horizontal_angle == 80)

    if at_extreme:
        # Move vertical servo from 0° to 30°
        for v_angle in range(0, 31, 1):
            vertical_angle = move_servo(VERTICAL_SERVO_PIN, v_angle, speed=3)
        # Move vertical servo back from 30° to 0°
        for v_angle in range(30, -1, -1):
            vertical_angle = move_servo(VERTICAL_SERVO_PIN, v_angle, speed=3)
    else:
        # Keep vertical angle at current position (or reset to 0 if needed)
        vertical_angle = move_servo(VERTICAL_SERVO_PIN, vertical_angle, speed=3)

    return horizontal_angle, vertical_angle, direction, at_extreme

def servo_stop():
    print("Stopping servos...")
    pi.set_servo_pulsewidth(HORIZONTAL_SERVO_PIN, 0)
    pi.set_servo_pulsewidth(VERTICAL_SERVO_PIN, 0)
    pi.stop()
    print("Servos stopped.")

if __name__ == "__main__":
    try:
        servo_init()
        horizontal_angle = 0
        vertical_angle = 0
        direction = 1
        for _ in range(100):  # Test 10 steps
            horizontal_angle, vertical_angle, direction, at_extreme = servo_move(horizontal_angle, vertical_angle, direction)
            print(f"Horizontal: {horizontal_angle}°, Vertical: {vertical_angle}°, Direction: {direction}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nServo test interrupted.")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        servo_stop()
