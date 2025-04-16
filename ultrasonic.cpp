#include "ultrasonic.hpp"
#include <iostream>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>  // For time()

#define GPIO_ULTRASONIC_BASE 0x3F200000  // Base address for GPIO registers (Raspberry Pi 3)
#define GPIO_PIN_17 17        // GPIO 17 for Trigger
#define GPIO_PIN_18 18        // GPIO 18 for Echo

volatile unsigned *gpio_ultrasonic;

void setup() {
    int mem = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem < 0) {
        std::cerr << "Error: Unable to open /dev/mem!" << std::endl;
        exit(1);
    }

    gpio_ultrasonic = (volatile unsigned *)mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED, mem, GPIO_ULTRASONIC_BASE);
    if (gpio_ultrasonic == MAP_FAILED) {
        std::cerr << "Error: Memory mapping failed!" << std::endl;
        exit(1);
    }
    close(mem);

    // Set GPIO Pin 17 (Trigger) as output
    gpio_ultrasonic[GPIO_PIN_17 / 10] |= (1 << ((GPIO_PIN_17 % 10) * 3));

    // Set GPIO Pin 18 (Echo) as input
    gpio_ultrasonic[GPIO_PIN_18 / 10] &= ~(7 << ((GPIO_PIN_18 % 10) * 3));
}

void pulseTrigger() {
    // Set Trigger High
    gpio_ultrasonic[GPIO_PIN_17 / 10] |= (1 << ((GPIO_PIN_17 % 10) * 3));

    usleep(10); // 10 microseconds

    // Set Trigger Low
    gpio_ultrasonic[GPIO_PIN_17 / 10] &= ~(1 << ((GPIO_PIN_17 % 10) * 3));
}

double getDistance() {
    long startTime = 0, endTime = 0;

    // Send pulse to trigger
    pulseTrigger();

    // Wait for Echo to go high
    while (!(gpio_ultrasonic[GPIO_PIN_18 / 10] & (1 << ((GPIO_PIN_18 % 10) * 3)))) {
        startTime = time(NULL);
    }

    // Wait for Echo to go low
    while (gpio_ultrasonic[GPIO_PIN_18 / 10] & (1 << ((GPIO_PIN_18 % 10) * 3))) {
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
    return 0;
}

void ultrasonic_run() {
    double distance = getDistance();
    std::cout << "Distance: " << distance << " cm" << std::endl;
}
