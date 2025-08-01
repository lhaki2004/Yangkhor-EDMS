#!/usr/bin/env python3
"""
Synchronous Auto-tagging monitoring script for Docker environment
Run this inside the Mayan container to monitor auto-tagging progress
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

from django.apps import apps
from mayan.apps.tags.models import Tag, DocumentTag
from mayan.apps.documents.models import Document

def check_auto_tagging_status():
    """Check the status of auto-tagging"""
    print("🔍 Synchronous Auto-Tagging Monitor")
    print("=" * 50)
    
    # Get recent documents
    recent_docs = Document.objects.filter(
        date_added__gte=datetime.now() - timedelta(hours=1)
    ).order_by('-date_added')
    
    print(f"📄 Recent documents (last hour): {recent_docs.count()}")
    
    # Check for auto-tagged documents
    auto_tagged_count = 0
    for doc in recent_docs:
        tags = doc.tags.all()
        if tags.exists():
            auto_tagged_count += 1
            print(f"✅ Document: {doc.label}")
            print(f"   Tags: {', '.join([tag.label for tag in tags])}")
            print(f"   Added: {doc.date_added}")
            print()
    
    print(f"🎯 Auto-tagged documents: {auto_tagged_count}")
    
    # Check recent tags
    recent_tags = Tag.objects.filter(
        documenttag__created__gte=datetime.now() - timedelta(hours=1)
    ).distinct()
    
    print(f"🏷️  Recent tags created: {recent_tags.count()}")
    for tag in recent_tags:
        print(f"   - {tag.label}")
    
    # Check settings
    from django.conf import settings
    print(f"\n⚙️  Auto-tagging settings:")
    print(f"   Enabled: {getattr(settings, 'AUTO_TAG_ENABLED', False)}")
    print(f"   API URL: {getattr(settings, 'AUTO_TAG_API_URL', 'http://localhost:8080/predict')}")
    print(f"   Timeout: {getattr(settings, 'AUTO_TAG_TIMEOUT', 30)}s")

def check_logs_for_auto_tag():
    """Check log files for auto-tagging activity"""
    print("\n📋 Recent Auto-Tag Logs:")
    print("=" * 50)
    
    log_files = [
        '/var/log/mayan/mayan.log',
        '/var/log/mayan/celery.log',
        '/var/log/celery.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 Checking: {log_file}")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Get last 20 lines containing auto-tag
                    auto_tag_lines = [line for line in lines[-50:] if 'auto.*tag' in line.lower() or 'auto_tag' in line]
                    for line in auto_tag_lines[-10:]:
                        print(f"   {line.strip()}")
            except Exception as e:
                print(f"   Error reading log: {e}")

if __name__ == "__main__":
    check_auto_tagging_status()
    check_logs_for_auto_tag()
    
    print("\n💡 To monitor in real-time:")
    print("   docker exec -it mayan-app-1 tail -f /var/log/mayan/mayan.log")
    print("\n💡 To test auto-tagging:")
    print("   1. Upload a document through the web interface")
    print("   2. Check the success message for auto-tagging results")
    print("   3. View the document to see attached tags") 