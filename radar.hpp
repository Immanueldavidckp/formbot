#ifndef RADAR_HPP
#define RADAR_HPP

int radar_init();     // If you want to call it separately (optional)
int radar_run();      // This will initialize, read, and print distance
void radar_close();   // Optional if you want to close separately

#endif
