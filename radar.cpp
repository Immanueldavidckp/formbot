#include "radar.hpp"
#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>

#define RADAR_I2C_ADDRESS 0x68
#define DISTANCE_REGISTER 0x00

int initRadarSensor() {
    int file = open("/dev/i2c-1", O_RDWR);
    if (file < 0) return -1;

    if (ioctl(file, I2C_SLAVE, RADAR_I2C_ADDRESS) < 0) {
        close(file);
        return -1;
    }

    return file;
}

int readRadarDistance(int file) {
    char buf[2];
    buf[0] = DISTANCE_REGISTER;
    if (write(file, buf, 1) != 1) return -1;
    if (read(file, buf, 2) != 2) return -1;
    return (buf[0] << 8) | buf[1];
}

void closeRadarSensor(int file) {
    close(file);
}

int radar_init (){

    initRadarSensor();
    readRadarDistance();
}
