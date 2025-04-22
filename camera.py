import os
import numpy as np
from tflite_runtime.interpreter import Interpreter
from picamera2 import Picamera2

class ObjectDetector:
    def __init__(self, model_path="coco_ssd.tflite", label_path="coco_labels.txt"):
        # Model initialization
        self.interpreter = Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load labels
        with open(label_path, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]
        
        # Camera setup (matches model input shape)
        input_shape = self.input_details[0]['shape']
        self.width, self.height = input_shape[2], input_shape[1]
        self.picam2 = Picamera2()
        self.config = self.picam2.create_preview_configuration(
            main={"size": (self.width, self.height), "format": "RGB888"},
            controls={"FrameRate": 5}
        )
    
    def start(self):
        """Initialize camera stream"""
        self.picam2.configure(self.config)
        self.picam2.start()
        print(f"Detection ready: Input {self.width}x{self.height}")
    
    def get_detections(self):
        """Capture and process one frame"""
        frame = self.picam2.capture_array()
        img = np.expand_dims(frame, axis=0).astype(np.uint8)
        
        # Run inference
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        
        # Process outputs (SSD MobileNet format)
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]
        
        return [
            {
                'label': self.labels[int(cls)],
                'confidence': float(score),
                'box': box.tolist()
            }
            for box, cls, score in zip(boxes, classes, scores)
            if score > 0.5
        ]
    
    def stop(self):
        """Release resources"""
        self.picam2.stop()
        print("Detection stopped")

# Example usage
if __name__ == "__main__":
    detector = ObjectDetector()
    detector.start()
    
    try:
        while True:
            detections = detector.get_detections()
            if detections:
                print("\nDetections:")
                for obj in detections:
                    print(f"{obj['label']}: {obj['confidence']:.2f}")
            else:
                print(".", end="", flush=True)  # Show activity when no detections
    except KeyboardInterrupt:
        detector.stop()  
