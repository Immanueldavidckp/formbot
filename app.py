from camera import ObjectDetector
from ultrasonic import UltrasonicSensor
from motor import MotorController
from gps import GPSSensor
from voice_control import VoiceController
import threading
import time

class RobotApplication:
    def __init__(self):
        print("Initializing robot components...")
        self.camera = ObjectDetector()
        self.ultrasonic = UltrasonicSensor(trigger_pin=23, echo_pin=24)
        self.motors = MotorController()
        self.gps = GPSSensor(port="/dev/ttyAMA4")
        self.voice = VoiceController(self.motors)
        
        self.running = True
        self.current_mode = "autonomous"  # or "voice"

        try:
            self.camera.start()
            if not self.gps.initialize():
                print("GPS initialization failed - continuing without GPS")
            
            # Start voice control thread
            self.voice_thread = threading.Thread(target=self._voice_control_loop)
            self.voice_thread.daemon = True
            self.voice_thread.start()
            
            print("All components ready!")
        except Exception as e:
            print(f"Initialization failed: {e}")
            self.cleanup()
            raise

    def _get_valid_detections(self):
        """Get detections with validated coordinates"""
        raw_detections = self.camera.get_detections()
        valid_detections = []

        for obj in raw_detections:
            box = [
                max(0.0, min(1.0, obj['box'][0])),
                max(0.0, min(1.0, obj['box'][1])),
                max(0.0, min(1.0, obj['box'][2])),
                max(0.0, min(1.0, obj['box'][3]))
            ]

            if (box[2] - box[0]) > 0.05 and (box[3] - box[1]) > 0.05:
                valid_detections.append({
                    'label': obj['label'],
                    'confidence': obj['confidence'],
                    'box': box
                })

        return valid_detections

    def _voice_control_loop(self):
        """Handle voice commands in background"""
        while self.running:
            try:
                command = self.voice.listen()
                
                # Mode switching
                if "voice control" in command:
                    self.current_mode = "voice"
                    print("\n=== SWITCHED TO VOICE CONTROL MODE ===")
                    continue
                elif "autonomous mode" in command:
                    self.current_mode = "autonomous"
                    print("\n=== SWITCHED TO AUTONOMOUS MODE ===")
                    continue
                
                # Process commands only in voice mode
                if self.current_mode == "voice":
                    if not self.voice.process_command(command):
                        print(f"Unknown command: {command}")
                
            except Exception as e:
                print(f"Voice control error: {e}")
                time.sleep(1)

    def run(self):
        try:
            while self.running:
                distance = self.ultrasonic.get_distance()
                detections = self._get_valid_detections()
                gps_data = self.gps.read_data()

                print("\n" + "="*40)
                print(f"MODE: {self.current_mode.upper()}")
                print(f"DISTANCE: {distance:.1f} cm")
                print(f"DETECTIONS: {len(detections)}")

                for i, obj in enumerate(detections, 1):
                    print(f"  {i}. {obj['label']}: {obj['confidence']:.2f} "
                          f"@ ({obj['box'][0]:.2f},{obj['box'][1]:.2f})-({obj['box'][2]:.2f},{obj['box'][3]:.2f})")

                if gps_data:
                    print(f"GPS: Lat={gps_data['latitude']:.6f}, Lon={gps_data['longitude']:.6f}")
                print("="*40)

                # Autonomous control logic
                if self.current_mode == "autonomous":
                    if distance < 20:
                        self.motors.emergency_stop()
                    elif detections:
                        self.motors.forward(speed=0.5)
                    else:
                        self.motors.stop()

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nShutdown requested...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Safe shutdown of all components"""
        self.running = False
        print("\nCleaning up resources...")
        self.camera.stop()
        self.ultrasonic.cleanup()
        self.motors.cleanup()
        self.gps.close()
        print("Robot shutdown complete")

if __name__ == "__main__":
    app = RobotApplication()
    app.run()
