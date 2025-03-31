# Appwrite EMF Calculator Architecture - PlantUML Diagram

This document contains PlantUML code for visualizing the architecture of the Appwrite EMF calculator application.

## System Architecture Overview

```plantuml
@startuml Appwrite Flow
title EMF Calculator + Appwrite Application Flow

' Initialization Flow
start
:User opens EMF Calculator application;
:Initialize Appwrite Client SDK;
:Set Appwrite project ID and endpoint;

' Authentication Flow
:User authenticates (if needed);
:Appwrite Client creates session;
:Validate authentication token;

' EMF Calculation Request Flow
:User enters EMF calculation parameters;
:Enter number of turns in coil;
:Enter wire radius (in centimeters);
:Enter magnetic field change (in teslas);
:Enter time of change (in seconds);
:Submit parameters to Appwrite Function;

' Server-side Processing Flow
:Appwrite routes request to function;
:Function receives request context;
:Validate input parameters;
:Convert radius from cm to meters;
:Calculate coil area (πr²);
:Calculate change in flux (ΔΦ = ΔB·A·N);
:Apply Faraday's law (ε = -N·ΔΦ/Δt);
:Generate plot of EMF over time;
:Format results as JSON response;
:Return EMF value and plot to client;

' Client-side Result Handling
:Client receives calculation results;
:Display calculated EMF value;
:Render EMF vs time plot;
:Allow user to save or share results;

stop

@enduml
```

## Function Execution Flow

```plantuml
@startuml Appwrite Function Flow
title EMF Calculator Function Execution Flow

' Function Invocation Flow
start
:Client application prepares EMF calculation parameters;
:Client calls Appwrite SDK's createExecution method;

' Server-side Function Processing
:Appwrite receives function execution request;
:Appwrite authenticates and authorizes the request;
:Appwrite routes to the EMF calculator function;
:Function runtime is initialized;
:Main function receives context object;

' Request Processing
:Parse request body from context.req;
:Extract EMF calculation parameters;
:Validate all required parameters are present;
:Validate parameter types and values;

' EMF Calculation Logic
:Initialize calculation variables;
:Convert radius from centimeters to meters;
:Calculate area of the coil (πr²);
:Calculate change in magnetic flux (ΔB·A·N);
:Apply Faraday's law (ε = -N·ΔΦ/Δt);
:Generate time points array;
:Calculate EMF at each time point;
:Create plot figure using matplotlib;
:Convert plot to base64 encoded image;

' Response Handling
:Prepare JSON response with EMF value and plot;
:Return response using context.res.json;
:Appwrite processes function response;
:Appwrite returns response to client;
:Client processes calculation results;
:Client displays EMF value and plot to user;

stop

@enduml
```

## Context Object Structure

```plantuml
@startuml Appwrite Context Flow
title Appwrite Function Context Object Structure and Flow

start
:Function is invoked with context object;

' Context Properties
:context.req - Contains request information;
note right: method, headers, body_json, body_text

:context.res - Contains response methods;
note right: json(), text(), empty()

:context.log() - For logging information;
note right: Visible only in Appwrite console

:context.error() - For logging errors;
note right: Visible only in Appwrite console

' Request Flow
:Access request data via context.req;
:Extract method (GET, POST, etc.);
:Parse request headers;
:Process body data (JSON or text);
:Validate input parameters;

' Processing Flow
:Execute business logic with validated data;
:Generate calculation results;
:Prepare response data;

' Response Flow
:Construct response using context.res methods;
:Choose appropriate response format (JSON/text);
:Set status code (200 for success, 4xx/5xx for errors);
:Set response headers if needed;
:Return response to Appwrite;

stop

@enduml
```

## EMF Calculator Data Flow

```plantuml
@startuml EMF Calculator Data Flow
title EMF Calculator Data Processing Flow

start

' Input Parameters 
:Receive input parameters;
note right: num_turns, radius, magnetic_field_change, time_interval

' Parameter Validation
:Validate parameters exist;
:Validate numeric values;
:Check for positive radius;
:Check for positive time interval;

' Unit Conversion
:Convert radius from cm to meters;
note right: radius / 100.0

' Area Calculation
:Calculate coil area;
note right: area = π × radius²

' Flux Calculation
:Calculate change in magnetic flux;
note right: ΔΦ = ΔB × area × num_turns

' EMF Calculation
:Apply Faraday's law;
note right: EMF = -ΔΦ/Δt

' Visualization
:Generate time points array;
:Calculate flux at each time point;
:Create EMF vs time plot;
:Convert plot to base64 string;

' Result Packaging
:Prepare results object;
:Include EMF value;
:Include base64 encoded plot;

stop

@enduml
```

## Appwrite CLI Workflow

```plantuml
@startuml Appwrite CLI Workflow
title Appwrite CLI Development Workflow

start

' Setup
:Install Node.js;
:Install Appwrite CLI;
note right: npm install -g appwrite-cli

' Configuration
:Initialize Appwrite project;
note right: appwrite init

:Login to Appwrite;
note right: appwrite login

' Function Development
:Create a new function;
note right: appwrite functions create

:Set up local development environment;
:Create main.py with EMF calculator code;
:Create requirements.txt;
note right: Include matplotlib, numpy, etc.

' Testing
:Test function locally;
note right: python test_locally.py

' Deployment
:Create deployment tag;
note right: appwrite functions createTag

:Wait for deployment to complete;
:Verify function status;
note right: appwrite functions get

' Execution
:Execute function with test parameters;
note right: appwrite functions execute

:Monitor function logs;
note right: appwrite functions logs

' Production Use
:Integrate function ID in client application;
:Configure client to call the function;
:Handle function responses in UI;

stop

@enduml

## Appwrite Serverless Function Internals

```plantuml
@startuml Appwrite Serverless Function Internals
title Appwrite Serverless Function - Detailed Internal Flow

start

' Function Initialization
:Appwrite receives function execution request;
:Appwrite validates project credentials;
:Appwrite checks function permissions;
:Appwrite prepares execution environment;
note right: Sets up container with appropriate runtime

' Function Runtime Setup
:Initialize Python runtime;
:Load function dependencies;
note right: From requirements.txt
:Import function code;
:Prepare context object;
note right: Includes req, res, env variables

' Function Execution
:Call main entry point function;
note right: main(context)
partition "Main Function Execution" {
  :Process function arguments;
  :Parse request parameters;
  
  partition "Request Handling (receive_emf_calculation_request)" {
    :Log received request;
    :Check for JSON body in request;
    :Extract and validate parameters;
    :Check for required parameters;
    :Validate parameter types;
    :Perform additional validation;
    note right: Radius > 0, Time interval > 0
  }
  
  partition "Business Logic (calculate_emf)" {
    :Extract validated parameters;
    note right: num_turns, radius, magnetic_field_change, time_interval
    :Convert radius from cm to meters;
    :Calculate coil area (πr²);
    :Calculate change in flux (ΔΦ = ΔB·A·N);
    :Apply Faraday's law (ε = -N·ΔΦ/Δt);
    
    :Generate visualization;
    partition "Plot Generation" {
      :Create time points array;
      :Calculate flux at each time point;
      :Create matplotlib figure;
      :Plot EMF over time;
      :Convert plot to bytes using BytesIO;
      :Encode plot as base64 string;
    }
  }
  
  partition "Response Handling (send_emf_calculation_response)" {
    :Check calculation success status;
    :Format JSON response;
    :Include EMF value in response;
    :Include base64 encoded plot in response;
    :Set appropriate status code;
    note right: 200 for success, 400/500 for errors
  }
}

' Function Completion
:Return response via context.res;
:Appwrite captures function output;
:Appwrite logs function execution details;
note right: Duration, memory usage, logs
:Appwrite processes response headers;
:Appwrite returns function result to client;

' Error Handling (parallel track)
detach
partition "Error Handling Paths" {
  :Function encounters error;
  :Log error via context.error();
  :Format error response;
  :Set appropriate error status code;
  :Return error response to Appwrite;
  :Appwrite returns error to client;
}

stop

@enduml
```

##  Python-based Appwrite Function Structure

This structural diagram describes the detailed process and architecture of the Python-based Appwrite function implementation for the EMF calculator. It illustrates the Python function's structure, components, and their interactions during the execution lifecycle.

```plantuml
@startuml Python Appwrite Function Structure

' Main Function Structure
package "EMF Calculator Function" as EMFFunction {
  class "Main Function" as MainFunction {
    + main(context)
    - validate_parameters(data)
    - calculate_emf(params)
    - generate_plot(time_points, emf_values)
    - create_response(emf, plot_b64)
  }

  class "Request Handler" as RequestHandler {
    + parse_request(context.req)
    + extract_body()
    + validate_content_type()
    - handle_json_body()
    - handle_form_data()
  }

  class "Parameter Validator" as ParamValidator {
    + validate_required_fields(data)
    + validate_numeric_values(data)
    + validate_positive_values(data)
    + convert_units(data)
  }

  class "EMF Calculator" as EMFCalculator {
    + calculate_area(radius)
    + calculate_flux_change(area, turns, field_change)
    + calculate_emf(flux_change, time)
    + generate_time_points(time_interval)
    + calculate_emf_over_time(flux_change, time_points)
  }

  class "Visualization Generator" as Visualizer {
    + create_plot(time_points, emf_values)
    + set_plot_style()
    + add_labels_and_title()
    + convert_to_base64()
  }

  class "Response Formatter" as ResponseFormatter {
    + create_success_response(emf, plot_b64)
    + create_error_response(message, status_code)
    + add_response_headers()
  }
}

' External Libraries
package "Python Libraries" as PythonLibs {
  class "NumPy" as NumPy {
    + array()
    + linspace()
    + pi
  }

  class "Matplotlib" as Matplotlib {
    + pyplot
    + Figure
    + savefig()
  }

  class "Base64" as Base64 {
    + b64encode()
    + b64decode()
  }

  class "JSON" as JSON {
    + dumps()
    + loads()
  }

  class "IO" as IO {
    + BytesIO
    + StringIO
  }
}

' Appwrite Runtime
package "Appwrite Function Runtime" as AppwriteRuntime {
  class "Context Object" as Context {
    + req
    + res
    + log()
    + error()
  }

  class "Request Object" as Request {
    + method
    + headers
    + query
    + body_raw
    + body_text
    + body_json
  }

  class "Response Methods" as Response {
    + json()
    + text()
    + send()
    + empty()
    + redirect()
  }
}

' Process Flow Relationships
MainFunction --> RequestHandler : "1. Passes context.req"
RequestHandler --> ParamValidator : "2. Sends extracted data"
ParamValidator --> EMFCalculator : "3. Provides validated parameters"
EMFCalculator --> NumPy : "4. Uses for calculations"
EMFCalculator --> Visualizer : "5. Passes calculation results"
Visualizer --> Matplotlib : "6. Creates visualization"
Visualizer --> IO : "7. Buffers plot data"
Visualizer --> Base64 : "8. Encodes plot image"
EMFCalculator --> ResponseFormatter : "9. Sends calculation results"
Visualizer --> ResponseFormatter : "10. Provides encoded plot"
ResponseFormatter --> JSON : "11. Formats response data"
ResponseFormatter --> Response : "12. Uses response methods"
Context --> MainFunction : "Provides execution context"
Context *-- Request : "Contains request data"
Context *-- Response : "Contains response methods"

' Error Handling Flows
RequestHandler ..> ResponseFormatter : "Error: Invalid request format"
ParamValidator ..> ResponseFormatter : "Error: Parameter validation failed"
EMFCalculator ..> ResponseFormatter : "Error: Calculation error"
Visualizer ..> ResponseFormatter : "Error: Plot generation failed"

note right of MainFunction
  Python Function Entry Point:
  
  def main(context):
      try:
          # Parse request data
          data = context.req.body_json
          
          # Validate parameters
          params = validate_parameters(data)
          
          # Calculate EMF
          emf, time_points, emf_values = calculate_emf(params)
          
          # Generate visualization
          plot_b64 = generate_plot(time_points, emf_values)
          
          # Return response
          return context.res.json(
              create_response(emf, plot_b64)
          )
      except Exception as e:
          context.error(str(e))
          return context.res.json(
              {"error": str(e)},
              status_code=400
          )
end note

note right of EMFCalculator
  EMF Calculation Process:
  
  1. Convert radius from cm to meters
  2. Calculate coil area: A = πr²
  3. Calculate flux change: ΔΦ = ΔB·A·N
  4. Apply Faraday's law: ε = -N·ΔΦ/Δt
  5. Generate time points array
  6. Calculate EMF at each time point
end note

@enduml
