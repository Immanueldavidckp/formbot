#ifndef CAMERA_HPP
#define CAMERA_HPP

#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <vector>
#include <string>

struct CameraContext {
    cv::dnn::Net net;
    std::vector<std::string> classNames;
    std::vector<std::string> outputLayerNames;
    cv::VideoCapture cap;
    float confThreshold;
    float nmsThreshold;
};

int camera_init(CameraContext& ctx);
void camera_run(CameraContext& ctx);

#endif
