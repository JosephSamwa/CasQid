import os
from django.conf import settings
from django.http import HttpResponse

def test_media_path(request):
    """
    Utility view to test if media files are accessible and correctly configured.
    Only available in DEBUG mode.
    """
    if not settings.DEBUG:
        return HttpResponse("This test view is only available in DEBUG mode.", status=403)
        
    # Check if the media root exists
    if not os.path.exists(settings.MEDIA_ROOT):
        return HttpResponse(f"MEDIA_ROOT directory does not exist: {settings.MEDIA_ROOT}", status=500)
    
    # Check if the partners directory exists inside media root
    partners_dir = os.path.join(settings.MEDIA_ROOT, 'partners')
    if not os.path.exists(partners_dir):
        os.makedirs(partners_dir)
        return HttpResponse(f"Created missing 'partners' directory at: {partners_dir}", status=200)
    
    # List all files in the partners directory
    try:
        partner_files = os.listdir(partners_dir)
        files_list = "<br>".join(partner_files) if partner_files else "No files found in partners directory."
        return HttpResponse(
            f"<h2>Media Configuration</h2>"
            f"<p>MEDIA_URL: {settings.MEDIA_URL}</p>"
            f"<p>MEDIA_ROOT: {settings.MEDIA_ROOT}</p>"
            f"<p>DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}</p>"
            f"<h3>Files in partners directory:</h3>"
            f"<p>{files_list}</p>"
        )
    except Exception as e:
        return HttpResponse(f"Error listing partner files: {str(e)}", status=500)
