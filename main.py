import time
import picamera
import io
import base64
import threading
import keyboard
import socket
from vl53l1x import vl53l1x_init, read_distance, vl53l1x_stop
from motor import motor_init, forward, reverse, turn_left, turn_right, u_turn, stop as motor_stop, cleanup as motor_cleanup
from servo import servo_init, servo_move, servo_stop
from gemini import detect_object, plan_path, chat_assistant
from path_plan import plan_path as plan_navigation

# Global variables for sensors, actuators, and data storage
camera = None
vl53 = None
stop_event = threading.Event()
run_data = []  # Store data from Autonomous Mode runs

def is_online(timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except (socket.error, socket.timeout):
        print("No internet connection detected. Skipping Gemini API calls...")
        return False

def initialize_system():
    global camera, vl53

    try:
        camera = picamera.PiCamera()
        camera.resolution = (640, 480)
        camera.start_preview()
        time.sleep(2)
        print("Camera initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        camera = None

    if vl53l1x_init():
        from vl53l1x import vl53 as vl53_obj
        vl53 = vl53_obj
        print("VL53L1X initialized successfully.")
    else:
        print("Continuing without VL53L1X distance sensor.")

    motor_init()
    servo_init()

def cleanup_system():
    print("Cleaning up system resources...")
    if camera:
        camera.close()
        print("Camera closed.")
    vl53l1x_stop(vl53)
    servo_stop()
    motor_stop()
    motor_cleanup()
    print("All resources cleaned up.")

def capture_image():
    if not camera:
        return None
    stream = io.BytesIO()
    try:
        camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        image_data = stream.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None
    finally:
        stream.close()

def autonomous_mode():
    print("Entering Autonomous Mode... (Press Ctrl+C to return to mode selection)")
    servo_angles = {"horizontal": 0, "vertical": 0}
    servo_lock = threading.Lock()
    horizontal_angle = 0
    vertical_angle = 0
    direction = 1
    local_run_data = []
    sensor_failed = False
    consecutive_failures = 0  # Track consecutive sensor failures

    def servo_thread():
        nonlocal horizontal_angle, vertical_angle, direction
        while not stop_event.is_set():
            horizontal_angle, vertical_angle, direction, at_extreme = servo_move(horizontal_angle, vertical_angle, direction)
            with servo_lock:
                servo_angles["horizontal"] = horizontal_angle
                servo_angles["vertical"] = vertical_angle
            time.sleep(0.05)

    try:
        servo_t = threading.Thread(target=servo_thread)
        servo_t.start()

        last_detected_object = "unknown"
        scanning = False

        while not stop_event.is_set():
            # Read distance from VL53L1X, with error handling
            distance = None
            if not sensor_failed:
                distance = read_distance(vl53)
                if distance is None:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:  # Too many consecutive failures
                        print("VL53L1X sensor failed repeatedly. Disabling sensor...")
                        sensor_failed = True
                else:
                    consecutive_failures = 0  # Reset counter on successful read

            distance_str = f"{distance} mm" if distance is not None else "N/A"

            # Capture image and detect object (every 5 degrees), but only if online
            with servo_lock:
                horizontal_angle = servo_angles["horizontal"]
                vertical_angle = servo_angles["vertical"]
            if horizontal_angle % 5 == 0:
                image_base64 = capture_image()
                if not image_base64:
                    print("Failed to capture image. Skipping detection...")
                    time.sleep(1)
                    continue
                if is_online():
                    try:
                        detected_object = detect_object(image_base64)
                        print(f"Gemini API response: {detected_object}")
                        last_detected_object = detected_object if detected_object != "unknown" else last_detected_object
                    except Exception as e:
                        print(f"Error with Gemini API: {e}. Treating as offline...")
                        last_detected_object = "unknown (offline)"
                else:
                    last_detected_object = "unknown (offline)"

            # Store data for this run
            local_run_data.append({
                "object": last_detected_object,
                "horizontal_angle": horizontal_angle,
                "vertical_angle": vertical_angle,
                "distance": distance
            })

            # Check for obstacle within 300 mm, but only if sensor is working
            if not sensor_failed and distance is not None and distance < 300 and not scanning:
                print(f"Obstacle detected at {distance} mm at horizontal angle {horizontal_angle}°!")
                motor_stop()
                scanning = True
                try:
                    plan_navigation(vl53, servo_move, servo_angles, servo_lock, stop_event)
                except Exception as e:
                    print(f"Error in path planning: {e}. Continuing in Autonomous Mode...")
                scanning = False
                print("Resuming Autonomous Mode after obstacle handling...")
                continue
            else:
                # If sensor has failed, move forward cautiously as a fallback
                if sensor_failed and not scanning:
                    print("VL53L1X sensor unavailable. Moving forward cautiously...")
                    forward(duty_cycle=10)
                elif not scanning:
                    print("No obstacle within 300 mm. Moving forward...")
                    forward(duty_cycle=15)

            # Print status
            with servo_lock:
                print(f"Detected Object: {last_detected_object}, Horizontal Servo: {servo_angles['horizontal']}°, "
                      f"Vertical Servo: {servo_angles['vertical']}°, Distance: {distance_str}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Returning to mode selection...")
        stop_event.set()
        servo_t.join()
        run_data.append(local_run_data)
    except Exception as e:
        print(f"Error in Autonomous Mode: {e}")
        stop_event.set()
        servo_t.join()
        run_data.append(local_run_data)

def ai_chat_mode():
    print("Entering AI Chat Mode... (Type 'exit' to return to mode selection)")
    while True:
        query = input("Enter your farm-related query: ")
        if query.lower() == "exit":
            break

        if "last run" in query.lower() and "pest" in query.lower():
            if not run_data:
                print("Assistant: No data from previous runs available.")
                continue
            last_run = run_data[-1]
            pest_found = False
            pest_details = []
            for entry in last_run:
                if "pest" in entry["object"].lower():
                    pest_found = True
                    pest_details.append(f"Pest detected: {entry['object']} at horizontal angle {entry['horizontal_angle']}°, distance {entry['distance']} mm")
            if pest_found:
                response = "Yes, pests were found in the last run.\n" + "\n".join(pest_details)
            else:
                response = "No pests were found in the last run."
            print(f"Assistant: {response}")
        else:
            if is_online():
                response = chat_assistant(query)
                print(f"Assistant: {response}")
            else:
                print("Assistant: Cannot respond to queries offline. Please ask about the last run or reconnect to the internet.")

def remote_mode():
    print("Entering Remote Mode... (Type 'q' to return to mode selection)")
    print("Controls: w=Forward, s=Reverse, a=Left, d=Right, u=U-Turn, q=Return to Mode Selection")
    current_state = "stop"

    while True:
        key = input("Enter command (w, s, a, d, u, q): ").lower()
        if key == 'q':
            print("Returning to mode selection...")
            motor_stop()
            break
        elif key == 'w':
            print("Moving forward...")
            if current_state != "forward":
                forward(duty_cycle=15)
                current_state = "forward"
        elif key == 's':
            print("Moving reverse...")
            if current_state != "reverse":
                reverse(duty_cycle=15)
                current_state = "reverse"
        elif key == 'a':
            print("Turning left...")
            if current_state != "left":
                turn_left(duty_cycle=30)
                current_state = "left"
        elif key == 'd':
            print("Turning right...")
            if current_state != "right":
                turn_right(duty_cycle=30)
                current_state = "right"
        elif key == 'u':
            print("Performing U-turn...")
            if current_state != "u_turn":
                u_turn(duty_cycle=40)
                current_state = "u_turn"
        else:
            if current_state != "stop":
                print("Stopping motors...")
                motor_stop()
                current_state = "stop"

def mode_selection():
    while True:
        print("\nSelect Mode:")
        print("1. Autonomous Mode (Navigate using Gemini, VL53L1X, and camera)")
        print("2. AI Chat Mode (Farm-related queries)")
        print("3. Remote Mode (Control with W, S, A, D, U, Q)")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        stop_event.clear()

        if choice == "1":
            autonomous_mode()
        elif choice == "2":
            ai_chat_mode()
        elif choice == "3":
            remote_mode()
        elif choice == "4":
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        initialize_system()
        mode_selection()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Error in main program: {e}")
    finally:
        cleanup_system()
