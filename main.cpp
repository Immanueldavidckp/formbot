#include "radar.hpp"
#include "motor.hpp"
#include "ultrasonic.hpp"
#include "camera.hpp"
#include "gps.hpp"
#include <iostream>


int main() {
    std::cout<<"Starting Farmbot Application"<<std::endl;

    
    gps_init();
    ultrasonic_init();
    motor_init();
    camera_init();

    while(true){

        gps_run(int uart_fd);
        ultrasonic_run();
        camera_run();

    }

    return 0;
}
