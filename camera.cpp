#include "camera.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <fstream>

cv::VideoCapture cap;
cv::dnn::Net net;
std::vector<std::string> classNames;

// Function to load class names from file
std::vector<std::string> loadClassNames(const std::string& filePath) {
    std::vector<std::string> classNames;
    std::ifstream file(filePath);
    std::string line;
    while (std::getline(file, line)) {
        classNames.push_back(line);
    }
    return classNames;
}

int camera_init() {
    const float confThreshold = 0.3;
    const float nmsThreshold = 0.4;

    // Load class names
    classNames = loadClassNames("coco.names");

    // Load YOLOv4-tiny model
    net = cv::dnn::readNetFromDarknet("yolov4-tiny.cfg", "yolov4-tiny.weights");
    if (net.empty()) {
        std::cerr << "❌ Failed to load YOLOv4-tiny model!" << std::endl;
        return -1;
    }

    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);

    // Open camera
    cap.open(0, cv::CAP_V4L2);
    if (!cap.isOpened()) {
        std::cerr << "❌ Failed to open camera!" << std::endl;
        return -1;
    }

    std::cout << "🎥 Camera initialized successfully.\n";
    return 0;
}

int camera_run() {
    std::cout<<"entered camera_run"<<std::endl;
    const float confThreshold = 0.3;
    const float nmsThreshold = 0.4;

    // Capture frame
    cv::Mat frame;
    cap >> frame;
    if (frame.empty()) return -1;

    // Create input blob
    cv::Mat blob = cv::dnn::blobFromImage(frame, 1/255.0, cv::Size(416, 416), cv::Scalar(), true, false);
    net.setInput(blob);

    std::vector<cv::Mat> outputs;
    net.forward(outputs, net.getUnconnectedOutLayersNames());

    for (const auto& output : outputs) {
        std::cout<<"entered 1st forloop"<<std::endl;
        for (int i = 0; i < output.rows; ++i) {
            float confidence = output.at<float>(i, 4);
            std::cout<<"confidence"<<confidence<<std::endl;
            
            if (confidence >= confThreshold) {
                cv::Mat scores = output.row(i).colRange(5, output.cols);
                cv::Point classIdPoint;
                double maxClassScore;
                cv::minMaxLoc(scores, 0, &maxClassScore, 0, &classIdPoint);
                std::cout<<"maxckassScore"<<maxckassScore<<std::endl;

                if (maxClassScore > confThreshold) {
                    int centerX = static_cast<int>(output.at<float>(i, 0) * frame.cols);
                    int centerY = static_cast<int>(output.at<float>(i, 1) * frame.rows);
                    int width = static_cast<int>(output.at<float>(i, 2) * frame.cols);
                    int height = static_cast<int>(output.at<float>(i, 3) * frame.rows);
                    int classId = classIdPoint.x;

                    std::string label = (classId < classNames.size()) ? classNames[classId] : "Unknown";
                    std::cout << "✅ Detected: " << label
                              << " | Size: " << width << "x" << height
                              << " | Confidence: " << (maxClassScore * 100) << "%" << std::endl;
                }
            
            }else{
                std::cout<<"if condtion not running"<<std::endl;
            }
        }
    }

    return 0;
}
