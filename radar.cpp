#include "radar.hpp"
#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define RADAR_I2C_ADDRESS 0x68
#define DISTANCE_REGISTER 0x00

static int radar_fd = -1;  // File descriptor (static for internal use)

int radar_init() {
    radar_fd = open("/dev/i2c-1", O_RDWR);
    if (radar_fd < 0) {
        std::cerr << "❌ Failed to open I2C bus\n";
        return -1;
    }

    if (ioctl(radar_fd, I2C_SLAVE, RADAR_I2C_ADDRESS) < 0) {
        std::cerr << "❌ Failed to set I2C address for radar\n";
        close(radar_fd);
        radar_fd = -1;
        return -1;
    }

    return 0;
}

int radar_run() {
    if (radar_fd < 0) {
        if (radar_init() != 0) return -1;
    }

    char buf[2] = {DISTANCE_REGISTER};

    std::cout<<"values"<<buf[0]<<std::endl;

    if (write(radar_fd, buf, 1) != 1) {
        std::cerr << "❌ Radar write error\n";
        return -1;
    }

    if (read(radar_fd, buf, 2) != 2) {
        std::cerr << "❌ Radar read error\n";
        return -1;
    }

    int distance = (buf[0] << 8) | buf[1];
    std::cout << "📡 Radar Distance: " << distance << " units\n";
    return distance;
}

void radar_close() {
    if (radar_fd >= 0) {
        close(radar_fd);
        radar_fd = -1;
        std::cout << "🔌 Radar connection closed\n";
    }
}
