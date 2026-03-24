import sys
import traceback
sys.path.append('c:/Users/Administrator/Music/panchratna/backend')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
try:
    django.setup()
    from django.core.management import call_command
    call_command('makemigrations')
except Exception as e:
    traceback.print_exc(file=sys.stdout)
