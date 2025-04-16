#ifndef GPS_HPP
#define GPS_HPP

// Sets up UART for GPS (returns file descriptor or -1 on failure)
int setupgps();

// Reads and processes GPS data from the given UART file descriptor
void gps_run(int uart_fd);

// Initializes the GPS module and starts continuous reading
int gps_init();

#endif // GPS_HPP
