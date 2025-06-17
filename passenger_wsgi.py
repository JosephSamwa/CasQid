import os
import sys

# Get absolute path to project directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, 'travel_consultant')

# Add both directories to Python path
sys.path.insert(0, current_dir)
sys.path.insert(1, project_dir)

# Set up Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'travel_consultant.settings'

# Initialize WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()