import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.TRIG = trigger_pin
        self.ECHO = echo_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, False)
        time.sleep(1)

    def get_distance(self):
        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        pulse_start = time.time()
        while GPIO.input(self.ECHO) == 0:
            if time.time() - pulse_start > 0.1:
                return -1  # Timeout

        pulse_end = time.time()
        while GPIO.input(self.ECHO) == 1:
            if time.time() - pulse_end > 0.1:
                return -1  # Timeout

        return round((time.time() - pulse_start) * 17150, 2)

    def cleanup(self):
        GPIO.cleanup()
