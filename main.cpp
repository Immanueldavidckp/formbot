#include "radar.hpp"
#include "motor.hpp"
#include "ultrasonic.hpp"
#include "camera.hpp"
#include "gps.hpp"
#include <iostream>


int main() {
    std::cout<<"Starting Farmbot Application"<<std::endl;

    camera_init();
    gps_init();
    ultrasonic_init();
    motor_init();

    return 0;
}
