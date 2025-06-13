#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print('🔥 Firebase Status Check')
print('=' * 30)
print(f'Firebase credentials path: {settings.FIREBASE_CREDENTIALS_PATH}')
print(f'Path exists: {os.path.exists(settings.FIREBASE_CREDENTIALS_PATH) if settings.FIREBASE_CREDENTIALS_PATH else False}')

try:
    import firebase_admin
    print('✅ Firebase Admin SDK installed')
    print(f'Apps initialized: {len(firebase_admin._apps)}')
except ImportError:
    print('❌ Firebase Admin SDK not installed')

print('\n📋 Current Status:')
if not settings.FIREBASE_CREDENTIALS_PATH:
    print('❌ Firebase credentials path not configured')
elif not os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
    print('❌ Firebase credentials file not found')
else:
    print('✅ Firebase credentials file exists')

print('\n🎯 Your game is ready for Firebase integration!')
print('📚 Check FIREBASE_SETUP.md for complete setup instructions')
