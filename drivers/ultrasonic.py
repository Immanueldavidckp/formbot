import RPi.GPIO as GPIO
import time

# GPIO Pins
TRIG = 23
ECHO = 24

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    time.sleep(2)  # Sensor stabilization

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10µs pulse
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound (343m/s → cm)
    distance = round(distance, 2)
    return distance

if __name__ == "__main__":
    try:
        setup()
        while True:
            dist = get_distance()
            print(f"Distance: {dist} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
