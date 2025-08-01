#!/usr/bin/env python3
import requests
import tempfile
import os

def test_auto_tag_api():
    """Test the Auto-Tag API with a simple request"""
    
    # API URL
    api_url = "http://host.docker.internal:8080/predict"
    
    # Create a simple test file (text file for now)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
        tmp_file.write("This is a test memo document for auto-tagging.")
        tmp_file_path = tmp_file.name
    
    try:
        print(f"Testing Auto-Tag API: {api_url}")
        print(f"Using test file: {tmp_file_path}")
        
        # Send request
        with open(tmp_file_path, 'rb') as file_obj:
            files = {'files': ('test_memo.txt', file_obj, 'text/plain')}
            
            print("Sending POST request...")
            response = requests.post(api_url, files=files, timeout=30)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                results = response.json()
                print(f"API Response: {results}")
                
                # Extract tags
                suggested_tags = []
                for result in results:
                    print(f"Processing result: {result}")
                    if 'predicted_tag' in result and result['predicted_tag']:
                        suggested_tags.append(result['predicted_tag'])
                        print(f"Added tag: {result['predicted_tag']}")
                    elif 'error' in result:
                        print(f"API error: {result['error']}")
                
                print(f"Final extracted tags: {suggested_tags}")
                return suggested_tags
            else:
                print(f"Error response: {response.text}")
                return []
                
    except Exception as e:
        print(f"Error testing API: {e}")
        return []
    finally:
        # Clean up
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

if __name__ == "__main__":
    test_auto_tag_api() 