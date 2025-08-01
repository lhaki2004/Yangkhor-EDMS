#!/usr/bin/env python3
"""
Script to create a superuser in Mayan EDMS using Django's ORM.
This script should be run inside the Mayan EDMS Docker container.
"""

import os
import sys
import django

# Add the Mayan EDMS source to Python path
sys.path.insert(0, '/opt/mayan-edms/source')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mayan.settings.production')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Replace 'admin', 'luwang314@gmail.com', and 'adMin@2025!#' 
# with your desired credentials.
user = User.objects.create_user(
    username='admin', 
    email='luwang314@gmail.com', 
    password='adMin@2025!#'
)
user.is_superuser = True
user.is_staff = True
user.save()

print(f"Superuser '{user.username}' created successfully!")
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Superuser: {user.is_superuser}")
print(f"Staff: {user.is_staff}")
print(f"User ID: {user.id}")

# Exit the script
exit() 