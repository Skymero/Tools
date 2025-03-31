# EMF Calculator - Appwrite Function

This project calculates the induced electromotive force (EMF) in a coil based on Faraday's law of electromagnetic induction. It is designed to be deployed as an Appwrite Cloud Function.

## Overview

The function calculates the EMF induced in a coil when subjected to a changing magnetic field, following these steps:
1. Calculate the area of the coil
2. Calculate initial and final magnetic flux
3. Calculate change in flux
4. Apply Faraday's law to find the induced EMF

## Inputs

The function accepts a JSON payload with the following parameters:

- `num_turns`: Number of turns in the coil
- `radius`: Radius of the coil in meters
- `initial_magnetic_field`: Initial magnetic field strength in Tesla
- `final_magnetic_field`: Final magnetic field strength in Tesla
- `time_interval`: Time interval over which the magnetic field changes in seconds

## Outputs

The function returns a JSON response with:

- `emf`: The calculated induced EMF in Volts
- `plot`: A base64-encoded PNG image showing the EMF variation over time

## Deployment

### Prerequisites
- Appwrite Cloud account
- Appwrite CLI installed

### Steps to Deploy

1. Install the Appwrite CLI if you haven't already:
```
npm install -g appwrite-cli
```

2. Login to your Appwrite account:
```
appwrite login
```

3. Initialize the function:
```
appwrite init function
```

4. Deploy the function:
```
appwrite deploy function
```

## Testing

You can test the function by sending a POST request with the required parameters. Example using cURL:

```bash
curl -X POST \
  'https://[APPWRITE_ENDPOINT]/functions/[FUNCTION_ID]/executions' \
  -H 'X-Appwrite-Project: [PROJECT_ID]' \
  -H 'X-Appwrite-Key: [API_KEY]' \
  -H 'Content-Type: application/json' \
  -d '{
    "num_turns": 100,
    "radius": 0.05,
    "initial_magnetic_field": 0.2,
    "final_magnetic_field": 0.5,
    "time_interval": 0.1
  }'
```

## License

MIT
