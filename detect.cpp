#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>
#include <map>

// Global variables
cv::VideoCapture cap;
cv::dnn::Net net;

// COCO class names (80 classes)
const std::vector<std::string> COCO_CLASSES = {
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
};

int camera_init() {
    // Load YOLO model
    try {
        net = cv::dnn::readNet("model.onnx");
    } catch (const cv::Exception& e) {
        std::cerr << "❌ Failed to load model: " << e.what() << std::endl;
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

void printDetections(const cv::Mat& output, int frameWidth, int frameHeight) {
    const float confThreshold = 0.3;
    std::map<std::string, int> objectCounts;

    // Output should be 1xNx85 where 85 = (x,y,w,h,conf,80 class scores)
    float* data = (float*)output.data;
    
    for (int i = 0; i < output.rows; ++i) {
        float confidence = data[4];
        
        if (confidence >= confThreshold) {
            cv::Mat scores = output.row(i).colRange(5, 85);
            cv::Point classIdPoint;
            double maxClassScore;
            cv::minMaxLoc(scores, 0, &maxClassScore, 0, &classIdPoint);
            
            if (maxClassScore > confThreshold) {
                int classId = classIdPoint.x;
                if (classId < COCO_CLASSES.size()) {
                    objectCounts[COCO_CLASSES[classId]]++;
                }
            }
        }
        data += output.cols;  // Move to next detection
    }

    // Print detection results
    std::cout << "\n=== Frame Detection Results ===" << std::endl;
    std::cout << "Total objects detected: " << output.rows << std::endl;
    std::cout << "Valid detections (confidence > " << confThreshold << "): " << std::endl;
    
    for (const auto& pair : objectCounts) {
        std::cout << "- " << pair.first << ": " << pair.second << std::endl;
    }
    std::cout << "=============================\n" << std::endl;
}

int camera_run() {
    cv::Mat frame;
    if (!cap.read(frame)) {
        std::cerr << "❌ Failed to capture frame!" << std::endl;
        return -1;
    }

    // Create input blob (adjust size to your model's expected input)
    cv::Mat blob = cv::dnn::blobFromImage(frame, 1.0/255.0, cv::Size(640, 640), cv::Scalar(), true, false);
    net.setInput(blob);

    // Forward pass
    std::vector<cv::Mat> outputs;
    net.forward(outputs, net.getUnconnectedOutLayersNames());

    // Process and print detections
    if (!outputs.empty()) {
        printDetections(outputs[0], frame.cols, frame.rows);
    }

    return 0;
}

int main() {
    if (camera_init() != 0) {
        return -1;
    }

    while (true) {
        if (camera_run() != 0) {
            break;
        }
        
        // Add small delay to control output rate
        cv::waitKey(100);  // 100ms delay (10 FPS)
    }

    cap.release();
    return 0;
}