# Building an Appwrite Function: Step-by-Step Guide

## Introduction

This guide will walk you through creating and deploying an Appwrite function, similar to assembling a LEGO set. Each step builds upon the previous one, and by the end, you'll have a fully functional Appwrite function ready for deployment.

![Appwrite Logo](https://appwrite.io/images/appwrite.svg)

## Prerequisites

Before starting, ensure you have:

- [x] Appwrite account
- [x] Appwrite CLI installed
- [x] Python 3.7 or higher
- [x] Basic knowledge of Python programming

## Step 1: Setting Up Your Project Structure

Just like organizing your LEGO pieces before building, we need to set up a proper project structure.

```
your-appwrite-function/
├── main.py            # Main entry point
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

**Why this matters**: A clear project structure makes your code easier to maintain and deploy. Appwrite expects a specific structure to properly execute your function.

## Step 2: Creating the Entry Point

Every LEGO model starts with a base plate; similarly, our Appwrite function starts with an entry point.

```python
# main.py
def main(context):
    """
    Main entry point for the Appwrite function.
    
    Args:
        context: The Appwrite function context
        
    Returns:
        Appropriate response object
    """
    return context.res.json({
        "message": "Hello, Appwrite!"
    })
```

**Why this matters**: The `main` function is the entry point that Appwrite calls when your function is invoked. The `context` object provides everything you need to handle requests and responses.

## Step 3: Understanding the Context Object

The context object is like the instruction manual for your LEGO set. It contains all the information you need.

```python
def main(context):
    # Logging (only visible to developers in the Appwrite console)
    context.log("Function started")
    
    # Access request data
    method = context.req.method  # GET, POST, etc.
    headers = context.req.headers  # Request headers
    body_json = context.req.body_json  # Parsed JSON body
    body_text = context.req.body_text  # Raw body text
    
    # Handle errors
    context.error("Something went wrong")  # Log errors
    
    # Return responses
    return context.res.json({"success": True})  # JSON response
    # OR
    # return context.res.text("Hello")  # Text response
```

**Why this matters**: The `context` object is your interface with the Appwrite ecosystem. It provides standardized methods for handling requests, responses, and logging.

## Step 4: Creating a Request Handler Function

Like separating LEGO pieces by function, we'll create a dedicated function to handle incoming requests.

```python
def receive_request(context):
    """
    Handles incoming requests to the Appwrite function.
    
    Args:
        context: The Appwrite function context
        
    Returns:
        dict: Parsed and validated request data
    """
    try:
        # Check if we have a JSON body
        if not hasattr(context.req, 'body_json') or not context.req.body_json:
            # Try to parse body_text if available
            if hasattr(context.req, 'body_text') and context.req.body_text:
                data = json.loads(context.req.body_text)
            else:
                return {
                    'success': False,
                    'error': 'No request body provided'
                }
        else:
            data = context.req.body_json
            
        # Validate required parameters are present
        # ...validation logic...
        
        return {
            'success': True,
            'data': data
        }
    except Exception as e:
        context.error(f"Request handling error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
```

**Why this matters**: Separating request handling logic makes your code more maintainable and easier to test. It also ensures consistent validation across all requests.

## Step 5: Creating a Response Handler Function

In LEGO building, connecting pieces properly ensures stability. Similarly, properly formatting responses ensures reliable communication.

```python
def send_response(context, result):
    """
    Sends a properly formatted response back to the client.
    
    Args:
        context: The Appwrite function context
        result: The result data to send
        
    Returns:
        Appwrite response object
    """
    if not result.get('success', False):
        # Handle error response
        error_message = result.get('error', 'Unknown error')
        return context.res.json(
            {
                'success': False,
                'message': error_message
            },
            status_code=400
        )
    else:
        # Handle success response
        return context.res.json(
            {
                'success': True,
                'data': result.get('data', {})
            },
            status_code=200
        )
```

**Why this matters**: Consistent response formatting improves client-side development experience and makes debugging easier.

## Step 6: Implementing Business Logic

Now like assembling the main features of your LEGO model, we implement the actual business logic. Business logic refers to the core functionality that carries out the actual purpose of your function

```python
def process_data(data):
    """
    Processes the request data and performs the main business logic.
    
    Args:
        data: The validated request data
        
    Returns:
        dict: The processing results
    """
    try:
        # Your business logic here
        result = data['value'] * 2  # Just an example
        
        return {
            'success': True,
            'data': {
                'result': result
            }
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Processing error: {str(e)}"
        }
```

**Why this matters**: Separating business logic from request/response handling allows you to focus on the core functionality without worrying about input/output mechanisms.

## Step 7: Integrating Everything in the Main Function

Like connecting all LEGO sections to complete your model, we now connect all components in the main function.

```python
def main(context):
    """
    Main entry point for the Appwrite function.
    
    Args:
        context: The Appwrite function context
        
    Returns:
        Appwrite response object
    """
    try:
        # Log function start
        context.log("Function started")
        
        # Step 1: Handle the request
        request_result = receive_request(context)
        if not request_result['success']:
            return send_response(context, request_result)
            
        # Step 2: Process the data
        processing_result = process_data(request_result['data'])
        
        # Step 3: Send the response
        return send_response(context, processing_result)
    except Exception as e:
        context.error(f"Unhandled exception: {str(e)}")
        return context.res.json(
            {
                'success': False,
                'message': f"Server error: {str(e)}"
            },
            status_code=500
        )
```

**Why this matters**: This orchestration function creates a clear flow through your application, making it easier to understand and maintain.

## Step 8: Specifying Dependencies

Just like having all the right LEGO pieces, we need to specify our dependencies.

```
# requirements.txt
appwrite==2.0.0
numpy==1.24.3
matplotlib==3.7.1
```

**Why this matters**: Appwrite uses this file to install all required packages before running your function. Missing dependencies will cause your function to fail.

## Step 9: Testing Locally

Before presenting your completed LEGO model, you test it. Similarly, we should test our function locally.

Create a `test_locally.py` file:

```python
import json
from main import main

# Create a mock context object
class MockContext:
    class MockRequest:
        def __init__(self, body_json=None):
            self.body_json = body_json
            self.method = "POST"
            
    class MockResponse:
        def json(self, content, status_code=200):
            return {
                "status_code": status_code,
                "body": content
            }
    
    def __init__(self, req_body=None):
        self.req = self.MockRequest(req_body)
        self.res = self.MockResponse()
        
    def log(self, message):
        print(f"LOG: {message}")
        
    def error(self, message):
        print(f"ERROR: {message}")

# Test data
test_data = {
    "value": 21
}

# Create mock context
mock_context = MockContext(test_data)

# Run function
result = main(mock_context)

# Print result
print(f"Status: {result['status_code']}")
print(f"Body: {json.dumps(result['body'], indent=2)}")
```

To run the test locally with PowerShell:

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the test
python test_locally.py
```

**Why this matters**: Local testing allows you to catch issues before deployment, saving time and preventing errors in production.

## Step 10: Deploying to Appwrite

Now, like displaying your finished LEGO model, we deploy our function to Appwrite.

1. Login to Appwrite CLI:
   ```powershell
   appwrite login
   ```

2. Initialize a function:
   ```powershell
   appwrite init function
   ```

3. Follow the prompts to set up your function name, runtime, etc.

4. Deploy the function:
   ```powershell
   appwrite push
   ```

**Why this matters**: Deployment makes your function available for use by your application or other Appwrite services.

## Step 11: Testing the Deployed Function

After deployment, use the Appwrite Console to test your function by executing it and reviewing the logs.

**Why this matters**: Even after local testing, it's important to verify that the function works correctly in the Appwrite environment.

## Step 12: Integrating with Your Application

Now that your function is ready, integrate it with your application:

```javascript
// JavaScript client example
import { Client, Functions } from 'appwrite';

const client = new Client()
    .setEndpoint('https://[APPWRITE_ENDPOINT]/v1')
    .setProject('[YOUR_PROJECT_ID]');

const functions = new Functions(client);

// Call your function
functions.createExecution(
    '[FUNCTION_ID]',
    JSON.stringify({
        value: 21
    }),
    false  // Set to true for async execution
)
.then(response => {
    console.log(response);
})
.catch(error => {
    console.error(error);
});
```

To set up a JavaScript client application that uses Appwrite:

```powershell
# Install Appwrite SDK for JavaScript
npm install appwrite

# If you're using a framework like React or Vue
# Create a new app
npx create-react-app my-appwrite-app
cd my-appwrite-app

# Install Appwrite SDK
npm install appwrite

# Start the development server
npm start
```

**Why this matters**: The function is only useful when integrated with your application, forming a complete solution.

## Function Configuration

To ensure the function works correctly, you need to configure the following in your Appwrite Console:

1. Go to your project in the Appwrite Console
2. Navigate to Functions
3. Select your EMF calculator function
4. Under the "Settings" tab, configure:
   - Runtime: Python 3.9
   - Entrypoint: `src/main.py`
   - Build Commands: `pip install -r requirements.txt`
   - **Permissions**: Set to "Any" to allow guest access, or configure specific roles as needed
   - Timeout: 15 seconds (or adjust based on your needs)

### Important: Fixing Permission Errors

If you see the error: `User (role: guests) missing scope (execution.read)`, you need to:

1. Go to your Appwrite Console
2. Navigate to your project settings
3. Go to the Functions section
4. Select your EMF calculator function
5. Click on "Settings"
6. Under "Permissions", add:
   - `execution.read` for the "guests" role (if you want to allow guest access)
   - Or create appropriate API keys with the required permissions

Alternatively, if you want to restrict access:
1. Ensure users are properly authenticated
2. Use API keys with appropriate permissions
3. Set up team-based access control

Example using API key authentication in your client code:
```javascript
import { Client, Functions } from 'appwrite';

const client = new Client()
    .setEndpoint('https://your-appwrite-endpoint')
    .setProject('your-project-id')
    .setKey('your-api-key'); // Make sure this key has execution.read permission

const functions = new Functions(client);
```

## API Parameters

The EMF calculator accepts the following parameters in the request body:

| Parameter | Type | Description |
|-----------|------|-------------|
| num_turns | number | Number of turns in the coil (N) |
| radius | number | Wire radius in centimeters |
| magnetic_field_change | number | Change in magnetic field in teslas |
| time_interval | number | Time of change in seconds |

Example request body:
```json
{
    "num_turns": 100,
    "radius": 5,
    "magnetic_field_change": 0.5,
    "time_interval": 2
}
```

## Understanding the Structure: Why It Works This Way

The modular approach we've taken follows software engineering best practices:

1. **Separation of Concerns**: By dividing the function into request handling, business logic, and response formatting, we make the code easier to understand and maintain.

2. **Error Handling**: Comprehensive error handling at each stage ensures that failures are caught and reported appropriately.

3. **Testability**: The modular structure makes testing simpler, as each component can be tested in isolation.

4. **Scalability**: As your function grows in complexity, this structure scales well, allowing you to add new features without rewriting existing code.

5. **Consistency**: Following this pattern ensures that all your Appwrite functions have a consistent structure, making it easier for team members to work on different functions.

This approach may seem more complex than a simple monolithic function, but it provides significant benefits in maintainability, reliability, and developer experience as your application grows.

Just as a well-designed LEGO set has clear instructions and modular components that fit together seamlessly, a well-designed Appwrite function follows a clear structure that makes it easy to build, test, and maintain.
