import json
import base64
from PIL import Image
import io
from main import main

# Mock Appwrite context to simulate the Appwrite function environment
class MockContext:
    class MockRequest:
        def __init__(self, body_json=None, body_text=None, method="POST"):
            self.body_json = body_json
            self.body_text = body_text
            self.method = method
            self.headers = {}
    
    class MockResponse:
        def __init__(self):
            pass
            
        def text(self, content, status_code=200, headers=None):
            if headers is None:
                headers = {}
            return {
                "status_code": status_code,
                "headers": headers,
                "body": content
            }
            
        def json(self, content, status_code=200, headers=None):
            if headers is None:
                headers = {}
            return {
                "status_code": status_code,
                "headers": headers,
                "body": content
            }
            
        def empty(self, status_code=204, headers=None):
            if headers is None:
                headers = {}
            return {
                "status_code": status_code,
                "headers": headers,
                "body": ""
            }
            
    def __init__(self, req_body=None):
        if isinstance(req_body, dict):
            self.req = self.MockRequest(body_json=req_body)
        elif isinstance(req_body, str):
            self.req = self.MockRequest(body_text=req_body)
        else:
            self.req = self.MockRequest()
        
        self.res = self.MockResponse()
        self._logs = []
        self._errors = []
        
    def log(self, message):
        print(f"LOG: {message}")
        self._logs.append(message)
        
    def error(self, message):
        print(f"ERROR: {message}")
        self._errors.append(message)


# Test parameters
test_params = {
    'num_turns': 100,
    'radius': 0.05,  # 5 cm in meters
    'initial_magnetic_field': 0.2,  # Tesla
    'final_magnetic_field': 0.5,  # Tesla
    'time_interval': 0.1  # seconds
}

print("=== EMF Calculator Function Test ===")
print(f"Testing with parameters: {json.dumps(test_params, indent=2)}")
print("----------------------------------")

# Create mock context with test parameters
mock_context = MockContext(test_params)

# Execute the function
result = main(mock_context)

# Check if the response is successful
if result["status_code"] == 200:
    response_data = result["body"]
    print(f"\nEMF Calculation Results:")
    print(f"------------------------")
    print(f"Number of turns: {test_params['num_turns']}")
    print(f"Coil radius: {test_params['radius']} meters")
    print(f"Initial magnetic field: {test_params['initial_magnetic_field']} Tesla")
    print(f"Final magnetic field: {test_params['final_magnetic_field']} Tesla")
    print(f"Time interval: {test_params['time_interval']} seconds")
    print(f"------------------------")
    print(f"Calculated EMF: {response_data['emf']} Volts")
    
    # Save the plot as an image file
    if 'plot' in response_data:
        image_data = base64.b64decode(response_data['plot'])
        image = Image.open(io.BytesIO(image_data))
        image.save('emf_plot.png')
        print(f"Plot saved as 'emf_plot.png'")
else:
    print(f"Error: {result['body']['message'] if 'message' in result['body'] else 'Unknown error'}")
    print(f"Status code: {result['status_code']}")
