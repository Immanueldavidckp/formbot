import time
from camera.detect import CameraDetector
from sensors.ultrasonic import UltrasonicSensor
from motors.motor import MotorController

class RobotApplication:
    def __init__(self):
        # Initialize components
        self.camera = CameraDetector()
        self.ultrasonic = UltrasonicSensor(trigger_pin=23, echo_pin=24)
        self.motors = MotorController()
        
        # Shared state
        self.running = True
    
    def run(self):
        try:
            while self.running:
                # 1. Get sensor data
                distance = self.ultrasonic.get_distance()
                
                # 2. Process camera
                detections = self.camera.get_detections()
                
                # 3. Decision making
                self._control_logic(distance, detections)
                
                time.sleep(0.1)  # Control loop frequency
                
        except KeyboardInterrupt:
            self.stop()
    
    def _control_logic(self, distance, detections):
        """Core decision logic for the robot"""
        # Example: Stop if object too close
        if distance < 20:  # 20cm threshold
            self.motors.stop()
        else:
            # Move toward detected objects
            for obj in detections:
                if obj['label'] == 'person' and obj['confidence'] > 0.7:
                    self.motors.forward(speed=0.5)
    
    def stop(self):
        """Clean shutdown"""
        self.running = False
        self.camera.stop()
        self.ultrasonic.cleanup()
        self.motors.stop()

if __name__ == "__main__":
    app = RobotApplication()
    app.run()