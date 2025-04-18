#include "radar.hpp"
#include "motor.hpp"
#include "ultrasonic.hpp"
#include "camera.hpp"
#include "gps.hpp"
#include <iostream>


int main() {
    std::cout<<"Starting Farmbot Application"<<std::endl;

    int uart_data = gps_init(); 

    
  //  gps_init();
    ultrasonic_init();
    motor_init();
    radar_init();
    //camera_init();

    while(true){

        
      radar_run();
    //  gps_run(uart_data);

    //    ultrasonic_run();
      //  camera_run();

    }

    return 0;
}
