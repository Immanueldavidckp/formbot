#include "motor.hpp"
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <iostream>

#define GPIO_BASE 0x3F200000  // Raspberry Pi 4 GPIO base address
#define GPIO_LEN  0xB4        // Length of the memory region

#define MOTOR_A_RPWM_PIN 12    // RPWM pin for Motor A
#define MOTOR_A_LPWM_PIN 13    // LPWM pin for Motor A
#define MOTOR_A_R_EN_PIN 16    // R_EN pin for Motor A
#define MOTOR_A_L_EN_PIN 19    // L_EN pin for Motor A

#define MOTOR_B_RPWM_PIN 20    // RPWM pin for Motor B
#define MOTOR_B_LPWM_PIN 21    // LPWM pin for Motor B
#define MOTOR_B_R_EN_PIN 26    // R_EN pin for Motor B
#define MOTOR_B_L_EN_PIN 6     // L_EN pin for Motor B

#define PWM_RANGE 100          // PWM range (0-100 for 100% duty cycle)

volatile unsigned int *gpio;

void setupGPIO() {
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd == -1) {
        std::cerr << "Failed to open /dev/mem!" << std::endl;
        exit(1);
    }

    gpio = (volatile unsigned int *)mmap(NULL, GPIO_LEN, PROT_READ | PROT_WRITE, MAP_SHARED, mem_fd, GPIO_BASE);
    if (gpio == MAP_FAILED) {
        std::cerr << "Memory mapping failed!" << std::endl;
        close(mem_fd);
        exit(1);
    }

    close(mem_fd);
}

void pinMode(int pin, int mode) {
    int reg = pin / 10;
    int shift = (pin % 10) * 3;
    if (mode == 1) {
        gpio[reg] |= (1 << shift);  // Set as output
    } else {
        gpio[reg] &= ~(1 << shift);  // Set as input
    }
}

void digitalWrite(int pin, int value) {
    int reg = (pin / 32) + 7;
    int shift = pin % 32;
    if (value == 1) {
        gpio[reg] = (1 << shift);  // Set pin high
    } else {
        gpio[reg] = (1 << (shift + 16));  // Set pin low
    }
}

void pwmWrite(int pin, int dutyCycle) {
    int pwmValue = (dutyCycle * PWM_RANGE) / 100;
    digitalWrite(pin, pwmValue);  // Simulating PWM control
}

void setupMotorPins() {
    setupGPIO();

    pinMode(MOTOR_A_RPWM_PIN, 1);
    pinMode(MOTOR_A_LPWM_PIN, 1);
    pinMode(MOTOR_A_R_EN_PIN, 1);
    pinMode(MOTOR_A_L_EN_PIN, 1);

    pinMode(MOTOR_B_RPWM_PIN, 1);
    pinMode(MOTOR_B_LPWM_PIN, 1);
    pinMode(MOTOR_B_R_EN_PIN, 1);
    pinMode(MOTOR_B_L_EN_PIN, 1);

    digitalWrite(MOTOR_A_R_EN_PIN, 1);
    digitalWrite(MOTOR_A_L_EN_PIN, 1);
    digitalWrite(MOTOR_B_R_EN_PIN, 1);
    digitalWrite(MOTOR_B_L_EN_PIN, 1);
}

void setMotorSpeed(int motor, int speed) {
    int pwm_duty_cycle = speed;

    if (motor == 1) {
        pwmWrite(MOTOR_A_RPWM_PIN, pwm_duty_cycle);
        pwmWrite(MOTOR_A_LPWM_PIN, pwm_duty_cycle);
    } else if (motor == 2) {
        pwmWrite(MOTOR_B_RPWM_PIN, pwm_duty_cycle);
        pwmWrite(MOTOR_B_LPWM_PIN, pwm_duty_cycle);
    }
}

void stopMotors() {
    digitalWrite(MOTOR_A_RPWM_PIN, 0);
    digitalWrite(MOTOR_A_LPWM_PIN, 0);
    digitalWrite(MOTOR_B_RPWM_PIN, 0);
    digitalWrite(MOTOR_B_LPWM_PIN, 0);
}

void forward() {
    // Both motors move forward at 50% duty cycle
    setMotorSpeed(1, 50); // Motor A
    setMotorSpeed(2, 50); // Motor B
    std::cout << "Moving forward at 50% duty cycle." << std::endl;
}

void reverse() {
    // Both motors move in reverse at 50% duty cycle
    setMotorSpeed(1, -50); // Motor A
    setMotorSpeed(2, -50); // Motor B
    std::cout << "Moving in reverse at 50% duty cycle." << std::endl;
}

void rightTurn() {
    // Left motor runs forward 40%, right motor runs reverse 10%
    setMotorSpeed(1, 40);  // Motor A (Left) Forward
    setMotorSpeed(2, -10); // Motor B (Right) Reverse
    std::cout << "Turning right." << std::endl;
}

void leftTurn() {
    // Left motor runs reverse 10%, right motor runs forward 40%
    setMotorSpeed(1, -10); // Motor A (Left) Reverse
    setMotorSpeed(2, 40);  // Motor B (Right) Forward
    std::cout << "Turning left." << std::endl;
}

void uTurn() {
    // Left motor runs reverse 40%, right motor runs forward 40%
    setMotorSpeed(1, -40); // Motor A (Left) Reverse
    setMotorSpeed(2, 40);  // Motor B (Right) Forward
    std::cout << "Making a U-turn." << std::endl;
}

int motor_init() {
    // Setup GPIO pins
    setupMotorPins();

    // Test different movements
  /*  forward();
    sleep(3); // Move forward for 3 seconds

    reverse();
    sleep(3); // Move reverse for 3 seconds

    rightTurn();
    sleep(3); // Turn right for 3 seconds

    leftTurn();
    sleep(3); // Turn left for 3 seconds

    uTurn();
    sleep(3); // U-turn for 3 seconds

    // Stop the motors after the movements
    stopMotors(); */
    std::cout << "Motors init completed" << std::endl;

    return 0;
}
