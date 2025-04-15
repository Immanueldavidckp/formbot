#ifndef GPS_HPP
#define GPS_HPP

// Sets up UART for GPS (returns file descriptor or -1 on failure)
int setupGPS();

// Reads and processes GPS data from the given UART file descriptor
void readinit(int uart_fd);

// Initializes the GPS module and starts continuous reading
int gps_init();

#endif // GPS_HPP
