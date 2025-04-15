#ifndef MOTOR_HPP
#define MOTOR_HPP

// Motor pin setup
void setupMotorPins();

// Motor control
void forward();
void reverse();
void leftTurn();
void rightTurn();
void uTurn();
void stopMotors();

// Internal functions (optional to expose)
void setMotorSpeed(int motor, int speed); // motor = 1 for A, 2 for B

#endif // MOTO_HPP
