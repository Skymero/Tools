# ⚡ Python Starter Function

A serverless function for image processing using the WoundSize repository. This function receives image data directly in the request payload, processes it using a cloned image processing repository, and uploads the results to Appwrite Storage.

## 🧰 Usage

### POST /

Processes an image sent directly in the request payload and returns the ID of the processed image stored in Appwrite Storage.

**Request Body**

```json
{
  "imageData": "base64_encoded_image_string",
  "metadata": {
    "fileName": "wound_image.jpg",
    "fileType": "image/jpeg",
    "additionalInfo": {
      "param1": "value1",
      "param2": "value2"
    }
  }
}
```

- `imageData`: Base64-encoded image string, optionally with data URL prefix (e.g., "data:image/jpeg;base64,...")
- `metadata`: Object containing metadata about the image
  - `fileName`: (Optional) Name of the file
  - `fileType`: (Optional) MIME type of the image
  - `additionalInfo`: (Optional) Additional metadata passed to the image processor

**Response**

Sample `200` Response:

```json
{
  "success": true,
  "processed_image_id": "unique-file-id",
  "message": "Image processed successfully"
}
```

Sample `400/500` Error Response:

```json
{
  "success": false,
  "message": "Error message explaining what went wrong"
}
```

### GET /ping

- Returns a "Pong" message.

**Response**

Sample `200` Response:

```text
Pong
```

## ⚙️ Configuration

| Setting           | Value                             |
| ----------------- | --------------------------------- |
| Runtime           | Python (3.9)                      |
| Entrypoint        | `src/main.py`                     |
| Build Commands    | `pip install -r requirements.txt` |
| Permissions       | `any`                             |
| Timeout (Seconds) | 15                                |

## 🔒 Environment Variables

The following environment variables are required:

| Variable              | Description                                                          |
| --------------------- | -------------------------------------------------------------------- |
| APPWRITE_ENDPOINT     | Appwrite endpoint URL (e.g., 'https://cloud.appwrite.io/v1')         |
| APPWRITE_PROJECT_ID   | The Appwrite project ID                                              |
| APPWRITE_API_KEY      | The Appwrite API key with storage permissions                        |
| REPO_URL              | The URL of the repository containing the image processing code       |
| STORAGE_BUCKET_ID     | ID of the storage bucket for processed images                        |

## 📋 Testing

To test the function locally:

1. Set the required environment variables
2. Run the manual test script: `python src/manual_main.py`

This will create a test image, convert it to base64, and call the main function with appropriate context.

## 📚 Implementation Details

- The function clones the WoundSize repository to access its image processing capabilities
- It expects the wound_analysis module from the cloned repo to have a main function that:
  - Takes a PIL.Image object as the first parameter
  - Accepts a metadata dictionary for additional parameters
  - Returns a processed PIL.Image object
