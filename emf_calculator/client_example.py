"""
Example client for the EMF Calculator Appwrite Function.

This script demonstrates how to call the EMF Calculator function 
from a Python client using the Appwrite SDK.
"""

import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from appwrite.client import Client
from appwrite.services.functions import Functions

def call_emf_calculator(endpoint, project_id, api_key, function_id, params):
    """
    Call the EMF Calculator Appwrite function.
    
    Args:
        endpoint (str): The Appwrite endpoint URL
        project_id (str): Your Appwrite project ID
        api_key (str): Your Appwrite API key
        function_id (str): The ID of the EMF Calculator function
        params (dict): The parameters for the EMF calculation
        
    Returns:
        dict: The function response with EMF value and plot
    """
    # Initialize the Appwrite client
    client = Client()
    client.set_endpoint(endpoint)
    client.set_project(project_id)
    client.set_key(api_key)
    
    # Initialize the Functions service
    functions = Functions(client)
    
    try:
        # Call the function with the parameters
        print("Calling EMF Calculator function...")
        execution = functions.create_execution(
            function_id=function_id,
            data=json.dumps(params),
            async_execution=False
        )
        
        # Parse the response
        response = json.loads(execution.response)
        
        if response.get('success', False):
            print(f"EMF Calculation successful! EMF = {response['emf']} Volts")
            
            # If you want to display the plot
            if 'plot' in response:
                # Decode the base64 plot
                plot_data = base64.b64decode(response['plot'])
                
                # Create a plot from the image data
                plt.figure(figsize=(10, 6))
                img = plt.imread(BytesIO(plot_data), format='png')
                plt.imshow(img)
                plt.axis('off')
                plt.tight_layout()
                plt.show()
            
            return response
        else:
            print(f"Error: {response.get('message', 'Unknown error')}")
            return response
        
    except Exception as e:
        print(f"Error calling EMF Calculator function: {str(e)}")
        return {'success': False, 'message': str(e)}


if __name__ == "__main__":
    # Replace these values with your actual Appwrite credentials
    appwrite_endpoint = "https://[APPWRITE_ENDPOINT]/v1"
    appwrite_project_id = "[YOUR_PROJECT_ID]"
    appwrite_api_key = "[YOUR_API_KEY]"
    emf_calculator_function_id = "[FUNCTION_ID]"
    
    # Example parameters for EMF calculation
    emf_params = {
        "num_turns": 100,
        "radius": 0.05,  # 5 cm in meters
        "initial_magnetic_field": 0.2,  # Tesla
        "final_magnetic_field": 0.5,  # Tesla
        "time_interval": 0.1  # seconds
    }
    
    # Call the function
    result = call_emf_calculator(
        appwrite_endpoint,
        appwrite_project_id,
        appwrite_api_key,
        emf_calculator_function_id,
        emf_params
    )
    
    print(f"Function execution complete!")
