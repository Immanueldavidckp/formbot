#include "gps.hpp"
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <cstring>

#define GPS_UART "/dev/serial1"  // UART3 corresponds to /dev/serial1

int setupGPS() {
    // Open the UART3 device
    int uart_fd = open(GPS_UART, O_RDWR | O_NOCTTY | O_SYNC);
    if (uart_fd < 0) {
        std::cerr << "Error opening UART3!" << std::endl;
        return -1;
    }

    // Configure the UART3 settings
    struct termios options;
    tcgetattr(uart_fd, &options);
    cfsetispeed(&options, B9600);  // Set the baud rate to 9600
    cfsetospeed(&options, B9600);  // Set the baud rate to 9600
    options.c_cflag |= (CLOCAL | CREAD);  // Enable receiver, disable modem control
    tcsetattr(uart_fd, TCSANOW, &options);

    return uart_fd;
}

void readgps(int uart_fd) {
    char buffer[256];
    int n = read(uart_fd, buffer, sizeof(buffer));  // Read data from UART3
    if (n > 0) {
        buffer[n] = '\0';  // Null-terminate the buffer
        std::cout << "GPS Data: " << buffer << std::endl;

        // Parsing the NMEA sentence to extract useful information
        if (strstr(buffer, "$GPGGA") != NULL) {
            // Parse the NMEA GGA sentence (Global Positioning System Fix Data)
            char lat[15], lon[15], alt[15];
            int hours, minutes, seconds;
            float latitude, longitude, altitude;

            // Extract latitude, longitude, and altitude from the GGA sentence
            sscanf(buffer, "$GPGGA,%*f,%s,%*c,%s,%*c,%*d,%*d,%*f,%s", lat, lon, alt);

            // Convert to float for lat, lon, and alt
            latitude = atof(lat);
            longitude = atof(lon);
            altitude = atof(alt);

            // Print the extracted values to the terminal
            std::cout << "Latitude: " << latitude << ", Longitude: " << longitude << ", Altitude: " << altitude << " meters" << std::endl;
        }
    }
}

int gps_init() {
    // Setup GPS UART3
    int gps_fd = setupgps();
    if (gps_fd < 0) {
        return -1;
    }

    // Continuously read GPS data
  //  while (true) {
        readgps(gps_fd);
        usleep(1000000); // Wait 1 second before reading again
  //  }

  //  close(gps_fd);  // Close the file descriptor for UART3
    return 0;
}
