import main as my_module
import base64
import os
from PIL import Image
import io

# Create a mock context object
class MockContext:
    def __init__(self):
        self.req = {}
        self.res = MockResponse()
        self.logs = []
        self.errors = []
    
    def log(self, message):
        self.logs.append(message)
        print(f"LOG: {message}")
    
    def error(self, message):
        self.errors.append(message)
        print(f"ERROR: {message}")
    
    # Add get method to match the expected context structure
    def get(self, key, default=None):
        if key == 'req':
            return self.req
        return default

class MockResponse:
    def json(self, data, status_code=200):
        print(f"Response (status: {status_code}):")
        for key, value in data.items():
            print(f"  {key}: {value}")
        return data

# Function to convert an image file to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_string}"

# Create a test image if none exists
def create_test_image(path, size=(100, 100), color=(255, 0, 0)):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new('RGB', size, color=color)
    img.save(path)
    return path

# Main execution
if __name__ == "__main__":
    # Environment variables needed for the test
    os.environ['APPWRITE_ENDPOINT'] = 'https://cloud.appwrite.io/v1'
    os.environ['APPWRITE_PROJECT_ID'] = 'your_project_id'
    os.environ['APPWRITE_API_KEY'] = 'your_api_key'
    os.environ['STORAGE_BUCKET_ID'] = 'your_bucket_id'
    os.environ['REPO_URL'] = 'https://github.com/Skymero/WoundSize.git'
    
    # Create a test image if needed
    test_image_path = os.path.join(os.path.dirname(__file__), "..", "test", "test_image.jpg")
    if not os.path.exists(test_image_path):
        test_image_path = create_test_image(test_image_path)
    
    # Convert image to base64
    base64_image = image_to_base64(test_image_path)
    
    # Create context with payload
    context = MockContext()
    context.req = {
        'payload': {
            'imageData': base64_image,
            'metadata': {
                'fileName': 'test_image.jpg',
                'fileType': 'image/jpeg',
                'additionalInfo': {
                    'param1': 'value1',
                    'param2': 'value2'
                }
            }
        }
    }
    
    # Call main function
    print("Calling main function with direct image input...")
    my_module.main(context)
    
    print("\nTest completed. Check logs for details.")
