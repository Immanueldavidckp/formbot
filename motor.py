import RPi.GPIO as GPIO
import time

class MotorController:
    def __init__(self):
        # Configure your motor pins
        GPIO.setmode(GPIO.BCM)
        self.pins = {
            'left_fwd': 17,
            'left_bwd': 27,
            'right_fwd': 22,
            'right_bwd': 23
        }

        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    def forward(self, speed=0.8):
        """Move forward"""
        self._stop_all()
        GPIO.output(self.pins['left_fwd'], GPIO.HIGH)
        GPIO.output(self.pins['right_fwd'], GPIO.HIGH)

    def backward(self, speed=0.5):
        """Move backward"""
        self._stop_all()
        GPIO.output(self.pins['left_bwd'], GPIO.HIGH)
        GPIO.output(self.pins['right_bwd'], GPIO.HIGH)

    def _stop_all(self):
        """Stop all motors"""
        for pin in self.pins.values():
            GPIO.output(pin, GPIO.LOW)

    def emergency_stop(self):
        """Hard stop with brief reverse pulse"""
        for pin in self.pins.values():
            GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.2)
        self._stop_all()

    def cleanup(self):
        GPIO.cleanup()
