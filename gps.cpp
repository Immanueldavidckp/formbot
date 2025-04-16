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
    std::cout<<"gpsinit done"<<std::endl;
    return uart_fd;
}

int gps_init() {
    return setupgps();  // Just return the uart_fd
   
}

void gps_run(int uart_fd) {
    char buffer[256];
    int n = read(uart_fd, buffer, sizeof(buffer));

    if (n > 0) {
        buffer[n] = '\0';
        std::cout << "GPS Data: " << buffer << std::endl;

        if (strstr(buffer, "$GPRMC")) {
            char time[11], status, lat[15], lat_dir, lon[15], lon_dir, date[7];
            sscanf(buffer, "$GPRMC,%10[^,],%c,%[^,],%c,%[^,],%c,%*[^,],%*[^,],%6[^,]",
                   time, &status, lat, &lat_dir, lon, &lon_dir, date);

            float latitude = atof(lat);
            float longitude = atof(lon);

            std::cout << "Time: " << time
                      << " | Status: " << status
                      << " | Latitude: " << latitude << " " << lat_dir
                      << " | Longitude: " << longitude << " " << lon_dir
                      << " | Date: " << date << std::endl;
        }
    }
}
