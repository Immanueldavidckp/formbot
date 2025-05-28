from motor import reverse, turn_left, turn_right, u_turn, stop as motor_stop, forward
from vl53l1x import read_distance

def plan_path(vl53, servo_move, servo_angles, servo_lock, stop_event):
    """
    Plan the next move based on VL53L1X readings at servo angles 0° to 80°.
    Args:
        vl53: VL53L1X sensor object
        servo_move: Function to move the servo
        servo_angles: Dict with current servo angles (thread-safe)
        servo_lock: Threading lock for servo angles
        stop_event: Threading event to stop the process
    Returns:
        None (executes motor commands directly)
    """
    readings = {}
    horizontal_angle = 0
    vertical_angle = 0
    direction = 1

    print("Scanning for obstacles at specific angles...")
    for target_angle in range(0, 81, 10):
        if stop_event.is_set():
            break
        while abs(horizontal_angle - target_angle) > 1:
            if stop_event.is_set():
                break
            horizontal_angle, vertical_angle, direction, _ = servo_move(horizontal_angle, vertical_angle, direction)
            with servo_lock:
                servo_angles["horizontal"] = horizontal_angle
                servo_angles["vertical"] = vertical_angle
            if direction == 1 and horizontal_angle >= target_angle:
                break
            elif direction == -1 and horizontal_angle <= target_angle:
                break

        distance = read_distance(vl53)
        readings[target_angle] = distance
        print(f"Distance at {target_angle}°: {distance if distance is not None else 'None'} mm")

    # Filter out None values and check if we have any valid readings
    valid_readings = {angle: dist for angle, dist in readings.items() if dist is not None}
    if not valid_readings:
        print("No valid distance readings obtained. Performing a U-turn as a fallback...")
        u_turn(duty_cycle=15)
        return

    # Find the lowest and highest values
    distances = list(valid_readings.values())
    angles = list(valid_readings.keys())
    lowest_distance = min(distances)
    highest_distance = max(distances)
    lowest_angle = angles[distances.index(lowest_distance)]
    print(f"Lowest distance: {lowest_distance} mm at {lowest_angle}°")
    print(f"Highest distance: {highest_distance} mm")

    # If lowest distance is under 150 mm, reverse until 300 mm
    if lowest_distance < 150:
        print("Obstacle too close (<150 mm)! Reversing until 300 mm...")
        max_retries = 20  # Maximum number of reverse attempts
        retry_count = 0
        invalid_reading_count = 0
        while lowest_distance < 300:
            if stop_event.is_set():
                break
            if retry_count >= max_retries:
                print("Max retries reached. Sensor may be failing. Performing a U-turn as a fallback...")
                u_turn(duty_cycle=15)
                return
            reverse(duty_cycle=15)
            time.sleep(0.5)  # Give some time for the vehicle to move
            horizontal_angle = lowest_angle
            with servo_lock:
                servo_angles["horizontal"] = horizontal_angle
            servo_move(horizontal_angle, vertical_angle, direction)
            lowest_distance = read_distance(vl53)
            retry_count += 1
            if lowest_distance is None:
                invalid_reading_count += 1
                if invalid_reading_count >= 5:  # Too many invalid readings
                    print("Too many invalid readings. Performing a U-turn as a fallback...")
                    u_turn(duty_cycle=15)
                    return
            else:
                invalid_reading_count = 0  # Reset counter if we get a valid reading
            print(f"Current distance: {lowest_distance if lowest_distance is not None else 'None'} mm")
        motor_stop()
        print(f"Reversed to {lowest_distance if lowest_distance is not None else 'unknown'} mm. Rechecking...")
        return plan_path(vl53, servo_move, servo_angles, servo_lock, stop_event)

    # Check where obstacles are (under 300 mm)
    below_40 = any(angle < 40 and valid_readings[angle] < 300 for angle in valid_readings)
    above_40 = any(angle >= 40 and valid_readings[angle] < 300 for angle in valid_readings)

    if below_40 and above_40:
        print("Obstacles on both sides! Performing U-turn...")
        u_turn(duty_cycle=15)
    elif below_40:
        print("Obstacle below 40°. Turning left...")
        turn_left(duty_cycle=15)
        forward(duty_cycle=15)
        time.sleep(1)
    elif above_40:
        print("Obstacle above 40°. Turning right...")
        turn_right(duty_cycle=15)
        forward(duty_cycle=15)
        time.sleep(1)
    else:
        print("No significant obstacles under 300 mm. Moving forward...")
        forward(duty_cycle=15)
