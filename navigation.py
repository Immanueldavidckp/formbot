import servo
import motor

def plan(value):
    """
    Plan the vehicle's next move based on distance and servo angle.
    """

    if value>100 :
        motor.forward()
    else :
        motor.stop()
    # Get the current servo angle
    servo_angle = servo.get_angle()

    # Read distance from VL53L1X sensor
    distance = servo.read_distance()

    print(f"Planning move: Distance={distance} mm, Servo Angle={servo_angle}°")

    # Decision-making logic
    if distance > 100:
        if 0 <= servo_angle <= 40:
            print("Turning right...")
            motor.turn_right()
        elif 40 < servo_angle <= 80:
            print("Turning left...")
            motor.turn_left()
    else:
        print("Performing U-turn...")
        motor.u_turn()
