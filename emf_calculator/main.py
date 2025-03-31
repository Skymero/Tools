import io
import base64
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from appwrite.client import Client
from appwrite.exception import AppwriteException
import os


def receive_emf_calculation_request(context):
    """
    Handles receiving and parsing EMF calculation requests from Appwrite clients.
    
    This function follows the Appwrite context pattern for receiving requests,
    validates input parameters, and returns them in a structured format.
    
    Args:
        context: The Appwrite function context object containing request data
        
    Returns:
        dict: Dictionary containing validated input parameters or error information
    """
    try:
        # Log the request received for debugging
        context.log("Received EMF calculation request")
        
        # Check if we have a JSON body in the request
        if not hasattr(context.req, 'body_json') or not context.req.body_json:
            # Try to parse the body text if body_json is not available
            if hasattr(context.req, 'body_text') and context.req.body_text:
                data = json.loads(context.req.body_text)
            else:
                return {
                    'success': False,
                    'error': 'No request body provided'
                }
        else:
            data = context.req.body_json
        
        # Log the parsed data
        context.log(f"Request data: {json.dumps(data)}")
        
        # Extract parameters with validation
        params = {}
        
        # Required parameters
        required_params = ['num_turns', 'radius', 'magnetic_field_change', 
                          'time_interval']
        
        # Validate all required parameters are present
        missing_params = [param for param in required_params if param not in data]
        if missing_params:
            return {
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}"
            }
        
        # Convert and validate parameters
        try:
            params['num_turns'] = float(data['num_turns'])
            params['radius'] = float(data['radius'])
            params['magnetic_field_change'] = float(data['magnetic_field_change'])
            params['time_interval'] = float(data['time_interval'])
        except ValueError as e:
            return {
                'success': False,
                'error': f"Parameter conversion error: {str(e)}"
            }
        
        # Additional validation
        if params['radius'] <= 0:
            return {
                'success': False, 
                'error': 'Radius must be a positive value'
            }
        
        if params['time_interval'] <= 0:
            return {
                'success': False,
                'error': 'Time interval must be a positive value'
            }
        
        # Request is valid
        return {
            'success': True,
            'params': params
        }
        
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Invalid JSON in request body'
        }
    except Exception as e:
        context.error(f"Error processing request: {str(e)}")
        return {
            'success': False,
            'error': f"Request processing error: {str(e)}"
        }


def send_emf_calculation_response(context, calculation_result):
    """
    Sends the EMF calculation results back to the Appwrite client using the proper
    Appwrite response format.
    
    Args:
        context: The Appwrite function context object
        calculation_result: Dictionary containing calculation results or error information
        
    Returns:
        The appropriate Appwrite response object
    """
    try:
        if not calculation_result.get('success', False):
            # Handle error response
            error_message = calculation_result.get('error', 'Unknown error occurred')
            context.error(f"Sending error response: {error_message}")
            
            # Return error response using Appwrite context.res.json()
            return context.res.json(
                {
                    'success': False,
                    'message': error_message
                },
                status_code=400
            )
        else:
            # Handle successful calculation
            context.log("Sending successful EMF calculation response")
            
            # Extract the calculation results
            emf = calculation_result.get('emf')
            plot_base64 = calculation_result.get('plot')
            
            # Return success response using Appwrite context.res.json()
            return context.res.json(
                {
                    'success': True,
                    'emf': emf,
                    'plot': plot_base64
                },
                status_code=200
            )
            
    except Exception as e:
        context.error(f"Error sending response: {str(e)}")
        return context.res.json(
            {
                'success': False,
                'message': f"Error sending response: {str(e)}"
            },
            status_code=500
        )


def calculate_emf(params):
    """
    Calculates the induced EMF in a coil based on the input parameters.
    
    Args:
        params: Dictionary containing:
            - num_turns: Number of turns in the coil (N)
            - radius: Wire radius in centimeters
            - magnetic_field_change: Change in magnetic field in teslas
            - time_interval: Time of change in seconds
        
    Returns:
        dict: Dictionary containing calculation results or error information
    """
    try:
        # Extract parameters
        num_turns = params['num_turns']
        radius_cm = params['radius']
        magnetic_field_change = params['magnetic_field_change']
        time_interval = params['time_interval']
        
        # Convert radius from centimeters to meters
        radius = radius_cm / 100.0  # convert to meters
        
        # Calculate area of the coil (πr²)
        area = np.pi * radius**2  # in square meters
        
        # Calculate change in flux (ΔΦ = ΔB·A·N)
        delta_flux = magnetic_field_change * area * num_turns  # in Weber
        
        # Apply Faraday's law to calculate induced EMF (ε = -N·ΔΦ/Δt)
        # Note: The negative sign indicates the direction of the induced EMF (Lenz's law)
        emf = -delta_flux / time_interval  # in Volts
        
        # Generate plot of EMF over time
        # Create an array of time points
        time_points = np.linspace(0, time_interval, 100)
        
        # Linear change in magnetic field
        magnetic_field = np.linspace(0, magnetic_field_change, 100)
        
        # Calculate flux at each time point
        flux = magnetic_field * area * num_turns
        
        # Calculate EMF at each time point (derivative of flux)
        emf_values = -num_turns * area * np.gradient(magnetic_field, time_points)

        # Create the plot
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.plot(time_points, emf_values)
        ax.set_title('Induced EMF over Time')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('EMF (Volts)')
        ax.grid(True)

        # Save plot to a base64 encoded string for JSON transmission
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plot_base64 = base64.b64encode(buf.read()).decode('utf-8')
        
        # Return the calculation results
        return {
            'success': True,
            'emf': emf,
            'plot': plot_base64
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Calculation error: {str(e)}"
        }


def main(context):
    """
    Main Appwrite function entrypoint for EMF calculator.
    
    This function orchestrates the entire process:
    1. Receives and validates the request
    2. Performs the EMF calculation
    3. Sends the response back to the client
    
    Args:
        context: The Appwrite function context object
        
    Returns:
        The appropriate Appwrite response
    """
    try:
        # Set up logging
        context.log("EMF Calculator function started")
        
        # Optional: Initialize Appwrite client if needed for other Appwrite services
        # client = Client()
        # if 'APPWRITE_FUNCTION_PROJECT_ID' in os.environ:
        #     client.set_project(os.environ['APPWRITE_FUNCTION_PROJECT_ID'])
        #     if 'APPWRITE_API_KEY' in os.environ:
        #         client.set_key(os.environ['APPWRITE_API_KEY'])
        
        # Step 1: Receive and validate the request
        request_result = receive_emf_calculation_request(context)
        
        if not request_result['success']:
            return send_emf_calculation_response(context, request_result)
        
        # Step 2: Perform the EMF calculation
        calculation_result = calculate_emf(request_result['params'])
        
        # Step 3: Send the response
        return send_emf_calculation_response(context, calculation_result)
        
    except Exception as e:
        context.error(f"Unhandled exception: {str(e)}")
        return context.res.json(
            {
                'success': False,
                'message': f"Server error: {str(e)}"
            },
            status_code=500
        )
