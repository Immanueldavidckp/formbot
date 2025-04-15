#ifndef RADAR_HPP
#define RADAR_HPP

// Initialize the radar sensor, return file descriptor
int initRadarSensor();

// Read distance in cm from the radar sensor
int readRadarDistance(int file);

// Close the radar sensor
void closeRadarSensor(int file);

#endif
