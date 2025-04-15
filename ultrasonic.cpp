#include "ultrasonic.hpp"
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdio.h>
#include <stdlib.h>

#define GPIO_BASE 0x3F200000  // Base address for GPIO registers
#define GPIO_PIN_17 17        // GPIO 17 for Trigger
#define GPIO_PIN_18 18        // GPIO 18 for Echo

volatile unsigned *gpio;

void setup() {
    int mem = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem < 0) {
        std::cerr << "Error: Unable to open /dev/mem!" << std::endl;
        exit(1);
    }

    gpio = (volatile unsigned *)mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, mem, GPIO_BASE);
    if (gpio == MAP_FAILED) {
        std::cerr << "Error: Memory mapping failed!" << std::endl;
        exit(1);
    }
    close(mem);

    // Set GPIO Pin 17 (Trigger) as output
    gpio[GPIO_PIN_17 / 10] |= (1 << ((GPIO_PIN_17 % 10) * 3));

    // Set GPIO Pin 18 (Echo) as input
    gpio[GPIO_PIN_18 / 10] &= ~(7 << ((GPIO_PIN_18 % 10) * 3));
}

void pulseTrigger() {
    // Set Trigger High
    gpio[GPIO_PIN_17 / 10] |= (1 << ((GPIO_PIN_17 % 10) * 3));

    usleep(10); // 10 microseconds

    // Set Trigger Low
    gpio[GPIO_PIN_17 / 10] &= ~(1 << ((GPIO_PIN_17 % 10) * 3));
}

double getDistance() {
    long startTime = 0, endTime = 0;

    // Send pulse to trigger
    pulseTrigger();

    // Wait for Echo to go high
    while (!(gpio[GPIO_PIN_18 / 10] & (1 << ((GPIO_PIN_18 % 10) * 3)))) {
        startTime = time(NULL);
    }

    // Wait for Echo to go low
    while (gpio[GPIO_PIN_18 / 10] & (1 << ((GPIO_PIN_18 % 10) * 3))) {
        endTime = time(NULL);
    }

    // Calculate duration
    double pulseDuration = endTime - startTime;

    // Calculate distance (in cm)
    double distance = pulseDuration * 17150;
    return distance;
}

int ultrasonic_init() {
    setup();
    while (true) {
        double distance = getDistance();
        std::cout << "Distance: " << distance << " cm" << std::endl;
        usleep(1000000); // Wait 1 second before next measurement
    }
    return 0;
}
