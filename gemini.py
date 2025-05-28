import os
from dotenv import load_dotenv
import http.client
import time
from datetime import datetime, timedelta
import google.generativeai as genai

# Load the API key from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY not found in .env file")

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

REQUEST_COUNT_FILE = "request_count.txt"
DAILY_LIMIT = 200

def is_online(timeout=5):
    """
    Check if the system is online by attempting an HTTP connection to Google.
    Args:
        timeout: Time in seconds to wait for a response
    Returns:
        bool: True if online, False if offline
    """
    try:
        conn = http.client.HTTPConnection("www.google.com", timeout=timeout)
        conn.request("HEAD", "/")
        conn.close()
        return True
    except Exception as e:
        print(f"No internet connection detected: {e}. Skipping Gemini API calls...")
        return False

def update_request_count():
    """
    Update the request count for Gemini API calls, enforcing a daily limit.
    Returns:
        int: Total requests made today
    Raises:
        Exception: If daily request limit is exceeded
    """
    current_date = datetime.now().date()
    total_requests = 0
    last_reset = current_date.strftime("%Y-%m-%d")

    # Initialize the request count file if it doesn't exist
    if not os.path.exists(REQUEST_COUNT_FILE):
        try:
            with open(REQUEST_COUNT_FILE, "w") as f:
                f.write(f"{last_reset},0")
            os.chmod(REQUEST_COUNT_FILE, 0o666)  # Ensure the file is writable by all users
        except Exception as e:
            print(f"Error creating request_count.txt: {e}")
            raise

    # Read the current request count
    try:
        with open(REQUEST_COUNT_FILE, "r") as f:
            line = f.read().strip()
            if line:
                date_str, count = line.split(",")
                total_requests = int(count)
                last_reset = date_str
            else:
                raise ValueError("request_count.txt is empty")
    except Exception as e:
        print(f"Error reading request_count.txt: {e}")
        raise

    # Reset the count if the date has changed
    if last_reset != current_date.strftime("%Y-%m-%d"):
        total_requests = 0
        last_reset = current_date.strftime("%Y-%m-%d")

    total_requests += 1

    # Write the updated count back to the file
    try:
        with open(REQUEST_COUNT_FILE, "w") as f:
            f.write(f"{last_reset},{total_requests}")
    except Exception as e:
        print(f"Error writing to request_count.txt: {e}")
        raise

    print(f"Total requests made: {total_requests}")

    if total_requests > DAILY_LIMIT:
        raise Exception("Daily request limit exceeded for Gemini API.")

    return total_requests

def detect_object(image_base64):
    """
    Detect the most prominent object in the image using Gemini API.
    Args:
        image_base64: Base64-encoded image data
    Returns:
        str: Name of the detected object, or "unknown" if detection fails
    """
    if not is_online():
        return "unknown (offline)"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            update_request_count()
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                "I am using a Raspberry Pi with a camera to detect objects. "
                "Analyze the attached image and identify the most prominent object. "
                "Return only the name of the object (e.g., 'apple', 'car', 'tree') without any additional text."
            )
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            object_name = response.text.strip() if response.text else "unknown"
            return object_name
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error in Gemini API for object detection: {e}")
                return "unknown"

def plan_path(image_base64):
    """
    Plan a navigation path using Gemini API.
    Args:
        image_base64: Base64-encoded image data
    Returns:
        str: Suggested path, or fallback message if planning fails
    """
    if not is_online():
        return "No path suggestion available (offline)."

    max_retries = 3
    for attempt in range(max_retries):
        try:
            update_request_count()
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = "Analyze the image and suggest a navigation path for a small farm robot to avoid obstacles."
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            return response.text.strip() if response.text else "No path suggestion available."
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error in Gemini API for path planning: {e}")
                return "No path suggestion available."

def chat_assistant(query):
    """
    Answer farm-related queries using Gemini API.
    Args:
        query: User's query string
    Returns:
        str: Response from the API, or error message if the call fails
    """
    if not is_online():
        return "I couldn't generate a response due to being offline."

    max_retries = 3
    for attempt in range(max_retries):
        try:
            update_request_count()
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"As a farming assistant, answer the following query: {query}"
            response = model.generate_content([prompt])
            return response.text.strip() if response.text else "I couldn't generate a response."
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Quota exceeded, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error in Gemini API for chat: {e}")
                return "I couldn't generate a response due to an error."
