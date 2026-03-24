import sys
import traceback

sys.path.append('c:/Users/Administrator/Music/panchratna/backend')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

try:
    from django.core.management import call_command
    call_command('makemigrations')
except Exception as e:
    with open('c:/Users/Administrator/Music/panchratna/backend/trace_err.log', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
    print("Logged to trace_err.log")
