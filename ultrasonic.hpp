#ifndef ULTRASONIC_HPP
#define ULTRASONIC_HPP

// Initialize GPIO pins for ultrasonic sensor
void setup();

// Send a trigger pulse to the ultrasonic sensor
void pulseTrigger();

// Read and return the distance in cm from the ultrasonic sensor
double getDistance();

#endif // ULTRASONIC_HPP
