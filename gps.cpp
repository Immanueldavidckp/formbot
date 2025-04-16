#include "gps.hpp"
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <cstring>

#define GPS_UART "/dev/ttyAMA4"  // UART4 corresponds to /dev/serial1

int setupgps() {
    int uart_fd = open(GPS_UART, O_RDWR | O_NOCTTY | O_SYNC);
    if (uart_fd < 0) {
        std::cerr << "Error opening UART3!" << std::endl;
        return -1;
    }

    struct termios options;
    tcgetattr(uart_fd, &options);
    cfsetispeed(&options, B9600);
    cfsetospeed(&options, B9600);
    options.c_cflag |= (CLOCAL | CREAD);
    tcsetattr(uart_fd, TCSANOW, &options);

    return uart_fd;
}

int gps_init() {
    return setupgps();  // Just return the uart_fd
    std::cout<<"gpsinit done"<<std::endl;
}

void gps_run(int uart_fd) {
    char buffer[256];
    int n = read(uart_fd, buffer, sizeof(buffer));

    if (n > 0) {
        buffer[n] = '\0';
        std::cout << "GPS Data: " << buffer << std::endl;

        if (strstr(buffer, "$GPGGA") != NULL) {
            char lat[15], lon[15], alt[15];
            float latitude, longitude, altitude;

            sscanf(buffer, "$GPGGA,%*f,%[^,],%*c,%[^,],%*c,%*d,%*d,%*f,%[^,]", lat, lon, alt);

            latitude = atof(lat);
            longitude = atof(lon);
            altitude = atof(alt);

            std::cout << "Latitude: " << latitude
                      << ", Longitude: " << longitude
                      << ", Altitude: " << altitude << " meters" << std::endl;
        }
    }
}
