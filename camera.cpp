#include "camera.hpp"
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <fstream>

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
    const float confThreshold = 0.3;  // Lowered for testing
    const float nmsThreshold = 0.4;

    // Load class names
    std::vector<std::string> classNames = loadClassNames("coco.names");

    // Load YOLOv4-tiny model
    cv::dnn::Net net = cv::dnn::readNetFromDarknet("yolov4-tiny.cfg", "yolov4-tiny.weights");
    if (net.empty()) {
        std::cerr << "❌ Failed to load YOLOv4-tiny model!" << std::endl;
        return -1;
    }

    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);

    // Open camera
    cv::VideoCapture cap(0, cv::CAP_V4L2);
    if (!cap.isOpened()) {
        std::cerr << "❌ Failed to open camera!" << std::endl;
        return -1;
    }

    std::vector<std::string> outputLayerNames = net.getUnconnectedOutLayersNames();

    std::cout << "🎥 YOLOv4-tiny object detection started. Press Ctrl+C to stop.\n";

  //  while (true) {
        cv::Mat frame;
        cap >> frame;
   //     if (frame.empty()) continue;
        

        // Create input blob
        cv::Mat blob = cv::dnn::blobFromImage(frame, 1/255.0, cv::Size(416, 416), cv::Scalar(), true, false);
        net.setInput(blob);

        std::vector<cv::Mat> outputs;
        net.forward(outputs, outputLayerNames);

        for (const auto& output : outputs) {
            for (int i = 0; i < output.rows; ++i) {
                float confidence = output.at<float>(i, 4);

                if (confidence >= confThreshold) {
                    cv::Mat scores = output.row(i).colRange(5, output.cols);
                    cv::Point classIdPoint;
                    double maxClassScore;
                    cv::minMaxLoc(scores, 0, &maxClassScore, 0, &classIdPoint);

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
                } else {
                    // If confidence is below threshold, print this
                    std::cout << "❌ Low Confidence Detected Object (Below " << confThreshold * 100 << "% confidence)\n";
                }
            }
        }
    //}

    return 0;
}
