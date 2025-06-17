from django.shortcuts import render

def csrf_failure(request, reason=""):
    return render(request, 'security/csrf_failure.html', {'reason': reason})


def handler500(request):
    return render(request, 'security/500.html', status=500)

def handler503(request):
    return render(request, 'security/503.html', status=503)

def handler404(request, exception):
    return render(request, 'security/404.html', status=404)

