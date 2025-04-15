#include <iostream>
#include <fstream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

// Define the I2C address of the radar sensor
#define RADAR_I2C_ADDRESS 0x68  // Replace with your radar sensor's I2C address
#define DISTANCE_REGISTER 0x00  // Register address for distance (replace with correct register)

int main() {
    // Open I2C bus (usually /dev/i2c-1 on Raspberry Pi)
    int file = open("/dev/i2c-1", O_RDWR);
    if (file < 0) {
        std::cerr << "Failed to open the I2C bus." << std::endl;
        return 1;
    }

    // Set the radar sensor's I2C address
    if (ioctl(file, I2C_SLAVE, RADAR_I2C_ADDRESS) < 0) {
        std::cerr << "Failed to acquire bus access and/or talk to the radar sensor." << std::endl;
        close(file);
        return 1;
    }

    std::cout << "Radar sensor initialized. Reading distance..." << std::endl;

    while (true) {
        // Read data from the sensor register
        char buf[2];
        buf[0] = DISTANCE_REGISTER;  // Register to read distance
        if (write(file, buf, 1) != 1) {
            std::cerr << "Failed to write register address to the sensor." << std::endl;
            close(file);
            return 1;
        }

        // Read 2 bytes from the register (assuming the distance value is 2 bytes long)
        if (read(file, buf, 2) != 2) {
            std::cerr << "Failed to read data from the sensor." << std::endl;
            close(file);
            return 1;
        }

        // Combine the two bytes into a single 16-bit distance value (big-endian format)
        int distance = (buf[0] << 8) | buf[1];
        std::cout << "Distance: " << distance << " cm" << std::endl;

        sleep(1);  // Delay before the next reading
    }

    close(file);
    return 0;
}
