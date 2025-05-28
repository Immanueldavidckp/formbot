import RPi.GPIO as GPIO
import time

# Left driver pin setup
LEFT_RPWM = 12  # GPIO12 for Left motor forward
LEFT_LPWM = 13  # GPIO13 for Left motor reverse
LEFT_R_EN = 16  # GPIO16 for Left motor enable forward
LEFT_L_EN = 19  # GPIO19 for Left motor enable reverse

# Right driver pin setup
RIGHT_RPWM = 20  # GPIO20 for Right motor forward
RIGHT_LPWM = 21  # GPIO21 for Right motor reverse
RIGHT_R_EN = 26  # GPIO26 for Right motor enable forward
RIGHT_L_EN = 6   # GPIO6 for Right motor enable reverse

# PWM frequency (Hz)
PWM_FREQ = 500  # Recommended for L298N

# Global PWM instances
left_r_pwm = None
right_r_pwm = None
left_l_pwm = None
right_l_pwm = None

def motor_init():
    global left_r_pwm, right_r_pwm, left_l_pwm, right_l_pwm

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Set up pins
    GPIO.setup(LEFT_RPWM, GPIO.OUT)
    GPIO.setup(LEFT_LPWM, GPIO.OUT)
    GPIO.setup(LEFT_R_EN, GPIO.OUT)
    GPIO.setup(LEFT_L_EN, GPIO.OUT)

    GPIO.setup(RIGHT_RPWM, GPIO.OUT)
    GPIO.setup(RIGHT_LPWM, GPIO.OUT)
    GPIO.setup(RIGHT_R_EN, GPIO.OUT)
    GPIO.setup(RIGHT_L_EN, GPIO.OUT)

    # Enable motor driver
    GPIO.output(LEFT_R_EN, GPIO.HIGH)
    GPIO.output(LEFT_L_EN, GPIO.HIGH)
    GPIO.output(RIGHT_R_EN, GPIO.HIGH)
    GPIO.output(RIGHT_L_EN, GPIO.HIGH)

    # Initialize PWM for all pins
    left_r_pwm = GPIO.PWM(LEFT_RPWM, PWM_FREQ)   # Forward PWM for left motor
    right_r_pwm = GPIO.PWM(RIGHT_RPWM, PWM_FREQ) # Forward PWM for right motor
    left_l_pwm = GPIO.PWM(LEFT_LPWM, PWM_FREQ)   # Reverse PWM for left motor
    right_l_pwm = GPIO.PWM(RIGHT_LPWM, PWM_FREQ) # Reverse PWM for right motor

    # Start PWM with 0% duty cycle
    left_r_pwm.start(0)
    right_r_pwm.start(0)
    left_l_pwm.start(0)
    right_l_pwm.start(0)

    print("Motors initialized with PWM.")

def forward(duty_cycle=15):  # Reduced default duty cycle
    """
    Move forward at the specified duty cycle using PWM.
    """
    print(f"Moving forward at {duty_cycle}% duty cycle...")
    # Ensure reverse PWM is off
    left_l_pwm.ChangeDutyCycle(0)
    right_l_pwm.ChangeDutyCycle(0)
    # Set forward PWM to specified duty cycle
    left_r_pwm.ChangeDutyCycle(duty_cycle)
    right_r_pwm.ChangeDutyCycle(duty_cycle)

def reverse(duty_cycle=15):  # Reduced default duty cycle
    """
    Move reverse at the specified duty cycle using PWM.
    """
    print(f"Moving reverse at {duty_cycle}% duty cycle...")
    # Ensure forward PWM is off
    left_r_pwm.ChangeDutyCycle(0)
    right_r_pwm.ChangeDutyCycle(0)
    # Set reverse PWM to specified duty cycle
    left_l_pwm.ChangeDutyCycle(duty_cycle)
    right_l_pwm.ChangeDutyCycle(duty_cycle)

def turn_left(duty_cycle=15, duration=2):  # Reduced default duty cycle
    """
    Turn left: left motor reverse, right motor forward.
    """
    print(f"Turning left at {duty_cycle}% duty cycle...")
    left_r_pwm.ChangeDutyCycle(0)
    left_l_pwm.ChangeDutyCycle(duty_cycle)
    right_r_pwm.ChangeDutyCycle(duty_cycle)
    right_l_pwm.ChangeDutyCycle(0)
    time.sleep(duration)
    stop()

def turn_right(duty_cycle=15, duration=2):  # Reduced default duty cycle
    """
    Turn right: left motor forward, right motor reverse.
    """
    print(f"Turning right at {duty_cycle}% duty cycle...")
    left_r_pwm.ChangeDutyCycle(duty_cycle)
    left_l_pwm.ChangeDutyCycle(0)
    right_r_pwm.ChangeDutyCycle(0)
    right_l_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(duration)
    stop()

def u_turn(duty_cycle=15, duration=3):  # Reduced default duty cycle
    """
    Perform a U-turn: left motor forward, right motor reverse for a longer duration.
    """
    print(f"Performing U-turn at {duty_cycle}% duty cycle...")
    left_r_pwm.ChangeDutyCycle(duty_cycle)
    left_l_pwm.ChangeDutyCycle(0)
    right_r_pwm.ChangeDutyCycle(0)
    right_l_pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(duration)
    stop()

def stop():
    """
    Stop the motors by setting the duty cycle to 0%.
    """
    print("Stopping motors...")
    left_r_pwm.ChangeDutyCycle(0)
    right_r_pwm.ChangeDutyCycle(0)
    left_l_pwm.ChangeDutyCycle(0)
    right_l_pwm.ChangeDutyCycle(0)

def cleanup():
    """
    Clean up GPIO and stop PWM.
    """
    print("Cleaning up GPIO and stopping PWM...")
    stop()
    left_r_pwm.stop()
    right_r_pwm.stop()
    left_l_pwm.stop()
    right_l_pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up.")

if __name__ == "__main__":
    try:
        motor_init()
        forward(duty_cycle=15)  # Test at 15% duty cycle
        time.sleep(10)  # Move forward for 10 seconds
        stop()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cleanup()
