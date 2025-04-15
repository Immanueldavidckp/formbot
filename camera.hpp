#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <string>
#include <vector>

// Function to load class names from a given file path
std::vector<std::string> loadClassNames(const std::string& filePath);

// Function to initialize the camera and run YOLOv4-tiny object detection
int camera_init();

#endif // CAMERA_HPP
