import os
from dotenv import load_dotenv
import google.generativeai as genai
import time
import picamera
import io
import base64

# Load the API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file")
    exit(1)

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize the legacy camera
camera = picamera.PiCamera()
try:
    camera.resolution = (640, 480)  # Lower resolution for faster processing
    camera.start_preview()
    time.sleep(2)  # Camera warm-up time
    print("Camera initialized successfully.")
except Exception as e:
    print(f"Failed to initialize camera: {e}")
    exit(1)

# Capture an image
def capture_image():
    stream = io.BytesIO()
    try:
        camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        image_data = stream.read()
        return base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None
    finally:
        stream.close()

# Main logic
try:
    # Capture image
    image_base64 = capture_image()
    if not image_base64:
        print("Failed to capture image. Exiting...")
        exit(1)

    # Prepare prompt for Gemini
    prompt = (
        "I am using a Raspberry Pi with a camera to detect objects. "
        "Analyze the attached image and identify the most prominent object. "
        "Return only the name of the object (e.g., 'apple', 'car', 'tree') without any additional text."
    )

    # Send prompt and image to Gemini with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            object_name = response.text.strip()
            print(f"Detected Object: {object_name}")
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 23 * (2 ** attempt)
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error: {e}")
                break

except Exception as e:
    print(f"Error in main loop: {e}")
finally:
    camera.close()
    print("Camera closed.")
