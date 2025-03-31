import unittest
from unittest.mock import Mock, patch, MagicMock
import base64
from PIL import Image
import io
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import main

class TestMainFunction(unittest.TestCase):
    @patch('main.subprocess.run')
    @patch('main.sys.path.insert')
    @patch('main.os.path.exists')
    @patch('main.os.environ.get')
    @patch('main.Client')
    @patch('main.Image.open')
    @patch('main.base64.b64decode')
    def test_main_with_direct_input(self, mock_b64decode, mock_image_open, mock_client, 
                                   mock_environ_get, mock_path_exists, 
                                   mock_sys_path_insert, mock_subprocess_run):
        # Mock the base64 decode
        mock_image_bytes = b'fake_image_bytes'
        mock_b64decode.return_value = mock_image_bytes
        
        # Mock the PIL Image
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image
        
        # Mock the Appwrite client
        client_instance = Mock()
        storage_instance = Mock()
        mock_client.return_value = client_instance
        client_instance.set_endpoint = Mock()
        client_instance.set_project = Mock()
        client_instance.set_key = Mock()
        
        # Mock Storage service
        storage_instance.create_file.return_value = {'$id': 'processed_file_id'}
        
        # Set up Storage mock to be returned when storage is created
        from appwrite.services.storage import Storage
        Storage.return_value = storage_instance
        
        # Mock environment variables
        mock_environ_get.side_effect = lambda key, default=None: {
            'APPWRITE_ENDPOINT': 'https://cloud.appwrite.io/v1',
            'APPWRITE_PROJECT_ID': 'test_project_id',
            'APPWRITE_API_KEY': 'test_api_key',
            'REPO_URL': 'https://github.com/Skymero/WoundSize.git',
            'STORAGE_BUCKET_ID': 'test_bucket_id'
        }.get(key, default)

        # Mock the file existence check
        mock_path_exists.return_value = False

        # Mock the subprocess.run call
        mock_subprocess_run.return_value = Mock(returncode=0)

        # Mock the sys.path.insert call
        mock_sys_path_insert.return_value = None
        
        # Mock the wound_analysis module
        mock_wound_analysis = Mock()
        mock_wound_analysis.main.return_value = mock_image
        
        # Mock the import of wound_analysis
        import sys
        sys.modules['wound_analysis'] = mock_wound_analysis

        # Mock the context object with direct image input
        context = Mock()
        base64_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD"  # Sample base64 data
        context.req = {'payload': {
            'imageData': base64_image,
            'metadata': {
                'fileName': 'test_image.jpg',
                'fileType': 'image/jpeg',
                'additionalInfo': {'test_param': 'test_value'}
            }
        }}
        
        # Mock response object
        json_response = Mock()
        context.res.json.return_value = json_response

        # Call the main function
        result = main(context)

        # Verify the base64 decode was called correctly
        mock_b64decode.assert_called_once()
        
        # Verify that the image was opened correctly
        mock_image_open.assert_called_once()
        
        # Verify that the client was set up correctly
        client_instance.set_endpoint.assert_called_once_with('https://cloud.appwrite.io/v1')
        client_instance.set_project.assert_called_once_with('test_project_id')
        client_instance.set_key.assert_called_once_with('test_api_key')

        # Verify that the repository was cloned correctly
        mock_subprocess_run.assert_called()

        # Verify that the repository was added to the Python path
        mock_sys_path_insert.assert_called_once_with(0, '/tmp/cloned_repo/WoundSize/WoundSize')

        # Verify that the image processor was called with correct parameters
        mock_wound_analysis.main.assert_called_once_with(mock_image, metadata={'test_param': 'test_value'})

        # Verify that the file was created in storage
        storage_instance.create_file.assert_called_once()
        
        # Verify that the response was correct
        context.res.json.assert_called_once()
        
        # Clean up the mock module
        del sys.modules['wound_analysis']

if __name__ == '__main__':
    unittest.main()