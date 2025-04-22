import json
import os
import threading
import time
from camera import ObjectDetector
from ultrasonic import UltrasonicSensor
from motor import MotorController
from gps import GPSSensor

CONFIG_PATH = "farm_config.json"

class RobotApplication:
    def __init__(self):
        print("Initializing robot components...")
        self.camera = ObjectDetector()
        self.ultrasonic = UltrasonicSensor(trigger_pin=23, echo_pin=24)
        self.motors = MotorController()
        self.gps = GPSSensor(port="/dev/ttyAMA4")

        self.running = True
        self.current_mode = "autonomous"
        self.farm_config = {}

        self.camera.start()
        if not self.gps.initialize():
            print("GPS initialization failed - continuing without GPS")

        print("All components ready!")

        self.select_mode()
        self.load_or_set_coordinates()

    def select_mode(self):
        print("\n[MODE SELECTION] Default mode is 'autonomous'.")
        print("You have 15 seconds to change the mode...")
        print("Type: 'command' or 'remote' to change, or leave blank to stay in autonomous mode.")

        user_input = self._wait_for_input(15)
        if user_input.lower() == "command":
            self.current_mode = "command"
        elif user_input.lower() == "remote":
            self.current_mode = "remote"
        else:
            self.current_mode = "autonomous"

        print(f"\n>>> Selected mode: {self.current_mode.upper()}")

    def load_or_set_coordinates(self):
        if os.path.exists(CONFIG_PATH):
            print("\n[FARM COORDINATE] Existing farm layout found.")
            print("You have 15 seconds to change it, or leave to keep using saved coordinates.")

            user_input = self._wait_for_input(15)
            if user_input.strip():
                self._enter_new_coordinates()
            else:
                with open(CONFIG_PATH, "r") as file:
                    self.farm_config = json.load(file)
                print("Loaded saved farm boundary and points.")
        else:
            print("\n[FARM COORDINATE] No farm layout found. Please enter it.")
            self._enter_new_coordinates()

    def _enter_new_coordinates(self):
        points = ["North-East", "South-East", "South-West", "North-West"]
        boundary = []
        for point in points:
            lat = float(input(f"Enter latitude for {point}: "))
            lon = float(input(f"Enter longitude for {point}: "))
            boundary.append((lat, lon))

        start_lat = float(input("Enter START point latitude: "))
        start_lon = float(input("Enter START point longitude: "))
        finish_lat = float(input("Enter FINISH point latitude: "))
        finish_lon = float(input("Enter FINISH point longitude: "))

        self.farm_config = {
            "boundary": boundary,
            "start": (start_lat, start_lon),
            "finish": (finish_lat, finish_lon)
        }

        with open(CONFIG_PATH, "w") as file:
            json.dump(self.farm_config, file)

        print("Farm layout saved successfully!")

    def _wait_for_input(self, timeout_seconds):
        print(f"(Waiting {timeout_seconds}s for input...)")
        result = ""
        def get_input():
            nonlocal result
            result = input(">>> ").strip()

        input_thread = threading.Thread(target=get_input)
        input_thread.daemon = True
        input_thread.start()
        input_thread.join(timeout_seconds)

        return result

    def run(self):
        try:
            while self.running:
                distance = self.ultrasonic.get_distance()
                detections = self._get_valid_detections()
                gps_data = self.gps.read_data()

                print("\n" + "=" * 40)
                print(f"MODE: {self.current_mode.upper()}")
                print(f"DISTANCE: {distance:.1f} cm")
                print(f"DETECTIONS: {len(detections)}")

                for i, obj in enumerate(detections, 1):
                    print(f"  {i}. {obj['label']}: {obj['confidence']:.2f} "
                          f"@ ({obj['box'][0]:.2f},{obj['box'][1]:.2f})-({obj['box'][2]:.2f},{obj['box'][3]:.2f})")

                if gps_data:
                    print(f"GPS: Lat={gps_data['latitude']:.6f}, Lon={gps_data['longitude']:.6f}")
                print("=" * 40)

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

    def _get_valid_detections(self):
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

    def cleanup(self):
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
