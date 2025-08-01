#!/usr/bin/env python3
"""
Test script for auto-tagging functionality
Run this to test if auto-tagging is working properly
"""

import os
import sys
import django
import requests
import tempfile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

from django.conf import settings
from mayan.apps.documents.models import Document
from mayan.apps.tags.models import Tag

def test_auto_tag_settings():
    """Test if auto-tagging settings are properly configured"""
    print("🔧 Testing Auto-Tag Settings")
    print("=" * 40)
    
    print(f"AUTO_TAG_ENABLED: {getattr(settings, 'AUTO_TAG_ENABLED', 'NOT SET')}")
    print(f"AUTO_TAG_API_URL: {getattr(settings, 'AUTO_TAG_API_URL', 'NOT SET')}")
    print(f"AUTO_TAG_TIMEOUT: {getattr(settings, 'AUTO_TAG_TIMEOUT', 'NOT SET')}")

def test_auto_tag_api():
    """Test if the Auto-Tag API is accessible"""
    print("\n🌐 Testing Auto-Tag API")
    print("=" * 40)
    
    api_url = getattr(settings, 'AUTO_TAG_API_URL', 'http://localhost:8080/predict')
    
    try:
        # Test basic connectivity
        response = requests.get(api_url.replace('/predict', '/health'), timeout=5)
        print(f"API Health Check: {response.status_code}")
    except Exception as e:
        print(f"API Health Check Failed: {e}")
    
    try:
        # Test with a simple file
        test_file_content = b"This is a test document for auto-tagging."
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(test_file_content)
            tmp_file.flush()
            
            with open(tmp_file.name, 'rb') as file_obj:
                files = {'files': ('test.txt', file_obj, 'text/plain')}
                
                response = requests.post(api_url, files=files, timeout=30)
                print(f"API Test Response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"API Test Result: {result}")
                else:
                    print(f"API Test Error: {response.text}")
                    
    except Exception as e:
        print(f"API Test Failed: {e}")

def test_database():
    """Test database connectivity and recent documents"""
    print("\n🗄️ Testing Database")
    print("=" * 40)
    
    try:
        # Check recent documents
        recent_docs = Document.objects.all().order_by('-date_added')[:5]
        print(f"Recent documents: {recent_docs.count()}")
        
        for doc in recent_docs:
            tags = doc.tags.all()
            print(f"  - {doc.label}: {[tag.label for tag in tags]}")
        
        # Check tags
        all_tags = Tag.objects.all()
        print(f"Total tags in database: {all_tags.count()}")
        
    except Exception as e:
        print(f"Database test failed: {e}")

def test_upload_flow():
    """Test the upload flow"""
    print("\n📤 Testing Upload Flow")
    print("=" * 40)
    
    print("1. Upload a document through the web interface")
    print("2. Check the logs for auto-tagging messages:")
    print("   docker exec -it mayan-app-1 tail -f /var/log/mayan/mayan.log")
    print("3. Check if tags were created:")
    print("   docker exec -it mayan-app-1 python manage.py shell")
    print("   >>> from mayan.apps.tags.models import Tag")
    print("   >>> Tag.objects.all().count()")

if __name__ == "__main__":
    test_auto_tag_settings()
    test_auto_tag_api()
    test_database()
    test_upload_flow()
    
    print("\n💡 Next Steps:")
    print("1. Make sure your Auto-Tag service is running on port 8080")
    print("2. Upload a document through the web interface")
    print("3. Check the logs for auto-tagging activity")
    print("4. Verify tags appear on the uploaded document") 