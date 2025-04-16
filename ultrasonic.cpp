#include "ultrasonic.hpp"
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <time.h>

#define GPIO_ULTRASONIC_BASE 0x3F200000
#define BLOCK_SIZE 4096

#define GPFSEL0 0
#define GPSET0 7
#define GPCLR0 10
#define GPLEV0 13

#define TRIG 17
#define ECHO 18

volatile unsigned *gpio_ultrasonic;

void set_output(int pin) {
    gpio_ultrasonic[GPFSEL0 + pin / 10] &= ~(7 << ((pin % 10) * 3));
    gpio_ultrasonic[GPFSEL0 + pin / 10] |= (1 << ((pin % 10) * 3));
}

void set_input(int pin) {
    gpio_ultrasonic[GPFSEL0 + pin / 10] &= ~(7 << ((pin % 10) * 3));
}

void write_pin(int pin, int val) {
    if (val)
        gpio_ultrasonic[GPSET0] = (1 << pin);
    else
        gpio_ultrasonic[GPCLR0] = (1 << pin);
}

int read_pin(int pin) {
    return (gpio_ultrasonic[GPLEV0] & (1 << pin)) ? 1 : 0;
}

void pulseTrigger() {
    write_pin(TRIG, 0);
    usleep(2);
    write_pin(TRIG, 1);
    usleep(10);
    write_pin(TRIG, 0);
}

double getDistance() {
    struct timespec start, end;

    pulseTrigger();

    // Wait for ECHO HIGH with timeout
    struct timespec timeout_start;
    clock_gettime(CLOCK_MONOTONIC, &timeout_start);
    while (read_pin(ECHO) == 0) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if ((now.tv_sec - timeout_start.tv_sec) * 1000 +
            (now.tv_nsec - timeout_start.tv_nsec) / 1e6 > 200) {
            return -1;
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &start);

    // Wait for ECHO LOW with timeout
    clock_gettime(CLOCK_MONOTONIC, &timeout_start);
    while (read_pin(ECHO) == 1) {
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        if ((now.tv_sec - timeout_start.tv_sec) * 1000 +
            (now.tv_nsec - timeout_start.tv_nsec) / 1e6 > 200) {
            return -1;
        }
    }
    clock_gettime(CLOCK_MONOTONIC, &end);

    double duration = (end.tv_sec - start.tv_sec) * 1e6 +
                      (end.tv_nsec - start.tv_nsec) / 1e3;

    double distance = (duration * 0.0343) / 2;
    return distance;
}

int ultrasonic_init() {
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        std::cerr << "Error opening /dev/mem!" << std::endl;
        exit(1);
    }

    gpio_ultrasonic = (volatile unsigned *)mmap(NULL, BLOCK_SIZE, PROT_READ | PROT_WRITE,
                                                MAP_SHARED, mem_fd, GPIO_ULTRASONIC_BASE);
    if (gpio_ultrasonic == MAP_FAILED) {
        std::cerr << "Memory mapping failed!" << std::endl;
        exit(1);
    }

    close(mem_fd);

    set_output(TRIG);
    set_input(ECHO);

    std::cout << "Ultrasonic initialized using gpio_ultrasonic" << std::endl;
    return 0;
}

void ultrasonic_run() {
    std::cout << "entered Ultrasonic_run" << std::endl;
    double distance = getDistance();
    if (distance >= 0)
        std::cout << "Distance: " << distance << " cm" << std::endl;
    else
        std::cout << "Distance measurement failed." << std::endl;
}
