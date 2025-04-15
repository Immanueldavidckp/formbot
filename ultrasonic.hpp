#ifndef ULTRASONIC_HPP
#define ULTRASONIC_HPP

// Initialize GPIO pins for ultrasonic sensor
void setup();

// Send a trigger pulse to the ultrasonic sensor
void pulseTrigger();

// Read and return the distance in cm from the ultrasonic sensor
double getDistance();

// init the function
int ultrasonic_init();

//run the function
void ultrasonic_run();

#endif // ULTRASONIC_HPP
