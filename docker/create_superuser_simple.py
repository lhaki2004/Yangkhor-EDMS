#!/usr/bin/env python3
"""
Simple script to create a superuser in Mayan EDMS.
"""

import os
import sys
import django

# Set the correct Python path for Mayan EDMS
sys.path.insert(0, '/opt/mayan-edms/source')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')

# Setup Django
django.setup()

# Now import Django components
from django.contrib.auth import get_user_model

User = get_user_model()

try:
    # Create the superuser
    user = User.objects.create_user(
        username='admin', 
        email='luwang314@gmail.com', 
        password='adMin@2025!#'
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    print(f"✅ Superuser '{user.username}' created successfully!")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   User ID: {user.id}")
    
except Exception as e:
    print(f"❌ Error creating superuser: {e}")
    sys.exit(1) 