from camera import ObjectDetector
import time

def test_camera():
    print("Starting camera test...")
    detector = ObjectDetector()
    detector.start()
    
    try:
        test_duration = 10  # seconds
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            detections = detector.get_detections()
            
            if detections:
                print("\n=== Detections ===")
                for obj in detections:
                    print(f"{obj['label']}: {obj['confidence']:.2f} confidence")
                    print(f"Box: {obj['box']}")
            else:
                print(".", end="", flush=True)  # Progress indicator
            
            time.sleep(0.5)  # Slow down output
        
    finally:
        detector.stop()
        print("\nTest completed")

if __name__ == "__main__":
    test_camera()
