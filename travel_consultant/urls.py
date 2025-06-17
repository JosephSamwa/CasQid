from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
import mimetypes

# Ensure all video MIME types are registered
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/webm', '.webm')
mimetypes.add_type('video/ogg', '.ogv')
mimetypes.add_type('video/quicktime', '.mov')
# Add image MIME types to be safe
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/gif', '.gif')
mimetypes.add_type('image/svg+xml', '.svg')

# Custom serve function to handle MIME types correctly
def media_serve(request, path, document_root=None):
    response = serve(request, path, document_root)
    
    # Check if file is a video and set the correct MIME type
    if path.lower().endswith(('.mp4', '.webm', '.ogv', '.mov')):
        ext = path.split('.')[-1].lower()
        content_type = {
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'ogv': 'video/ogg',
            'mov': 'video/quicktime'
        }.get(ext, 'application/octet-stream')
        
        response['Content-Type'] = content_type
    
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('core.urls')),
    path('jobs/', include('jobs.urls')),
    path('applications/', include('applications.urls')),
    path('services/', include('services.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('contacts/', include('contact.urls')),  # Fixed the trailing slash
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('', include('appointments.urls')),
]

# Media files URL pattern - make this more explicit and ensure it's always included
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', media_serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Static files for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler500 = 'security.views.handler500'
handler503 = 'security.views.handler503'
handler404 = 'security.views.handler404'