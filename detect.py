import numpy as np
from tflite_runtime.interpreter import Interpreter
from picamera2 import Picamera2
import time

# Configuration
model_path = "detect.tflite"
labels_path = "labelmap.txt"
confidence_threshold = 0.5

# Load labels
with open(labels_path, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Initialize interpreter
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Get model input shape
input_shape = input_details[0]['shape']
height, width = input_shape[1], input_shape[2]
channels = input_shape[3]
print(f"Model expects input shape: {input_shape}")  # Debug

# Initialize camera - match model input size
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (width, height), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

try:
    frame_count = 0
    start_time = time.time()
    
    while True:
        # Capture frame (already in correct size)
        frame = picam2.capture_array()
        
        # Debug shape info
        print(f"Captured frame shape: {frame.shape}")  # Should be (height, width, 3)
        
        # Ensure correct shape and type
        if frame.shape[2] == 4:  # If RGBA image
            frame = frame[:, :, :3]  # Remove alpha channel
        
        # Add batch dimension and ensure correct type
        img = np.expand_dims(frame, axis=0).astype(np.uint8)
        
        # Verify final input shape
        print(f"Input tensor shape: {img.shape}")  # Should be (1, height, width, 3)
        
        # Run inference
        interpreter.set_tensor(input_details[0]['index'], img)
        interpreter.invoke()
        
        # Get results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0]
        classes = interpreter.get_tensor(output_details[1]['index'])[0]
        scores = interpreter.get_tensor(output_details[2]['index'])[0]
        
        # Clear terminal
        print("\033[H\033[J", end="")
        print(f"===== Detections (FPS: {frame_count/(time.time()-start_time):.1f}) =====")
        
        # Print detections
        for i in range(len(scores)):
            if scores[i] > confidence_threshold:
                print(f"{labels[int(classes[i])]}: {scores[i]:.2f} at "
                      f"({boxes[i][1]:.2f},{boxes[i][0]:.2f})-"
                      f"({boxes[i][3]:.2f},{boxes[i][2]:.2f})")
        
        frame_count += 1
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    picam2.stop()