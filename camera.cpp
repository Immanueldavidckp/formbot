#include "camera.hpp"
#include <iostream>
#include <fstream>

std::vector<std::string> loadClassNames(const std::string& filePath) {
    std::vector<std::string> classNames;
    std::ifstream file(filePath);
    std::string line;
    while (std::getline(file, line)) {
        classNames.push_back(line);
    }
    return classNames;
}

int camera_init(CameraContext& ctx) {
    ctx.confThreshold = 0.3f;
    ctx.nmsThreshold = 0.4f;

    ctx.classNames = loadClassNames("coco.names");

    ctx.net = cv::dnn::readNetFromDarknet("yolov4-tiny.cfg", "yolov4-tiny.weights");
    if (ctx.net.empty()) {
        std::cerr << "❌ Failed to load YOLOv4-tiny model!" << std::endl;
        return -1;
    }

    ctx.net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    ctx.net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);

    ctx.cap.open(0, cv::CAP_V4L2);
    if (!ctx.cap.isOpened()) {
        std::cerr << "❌ Failed to open camera!" << std::endl;
        return -1;
    }

    ctx.outputLayerNames = ctx.net.getUnconnectedOutLayersNames();

    std::cout << "✅ Camera initialized for YOLOv4-tiny object detection.\n";
    return 0;
}

void camera_run(CameraContext& ctx) {
    cv::Mat frame;
    ctx.cap >> frame;

    if (frame.empty()) return;

    cv::Mat blob = cv::dnn::blobFromImage(frame, 1/255.0, cv::Size(416, 416), cv::Scalar(), true, false);
    ctx.net.setInput(blob);

    std::vector<cv::Mat> outputs;
    ctx.net.forward(outputs, ctx.outputLayerNames);

    for (const auto& output : outputs) {
        for (int i = 0; i < output.rows; ++i) {
            float confidence = output.at<float>(i, 4);
            if (confidence >= ctx.confThreshold) {
                cv::Mat scores = output.row(i).colRange(5, output.cols);
                cv::Point classIdPoint;
                double maxClassScore;
                cv::minMaxLoc(scores, 0, &maxClassScore, 0, &classIdPoint);

                if (maxClassScore > ctx.confThreshold) {
                    int centerX = static_cast<int>(output.at<float>(i, 0) * frame.cols);
                    int centerY = static_cast<int>(output.at<float>(i, 1) * frame.rows);
                    int width   = static_cast<int>(output.at<float>(i, 2) * frame.cols);
                    int height  = static_cast<int>(output.at<float>(i, 3) * frame.rows);
                    int classId = classIdPoint.x;

                    std::string label = (classId < ctx.classNames.size()) ? ctx.classNames[classId] : "Unknown";
                    std::cout << "✅ Detected: " << label
                              << " | Size: " << width << "x" << height
                              << " | Confidence: " << (maxClassScore * 100) << "%" << std::endl;
                }
            }
        }
    }
}
