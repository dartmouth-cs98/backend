from django.shortcuts import render

def home(request):
    return render(request, "hindsite/index.html", {})

def home_files(request, filename):
    return render(request, filename, {}, content_type="text/plain")

def verification_file(request):
    return render(request, 'google0ace3af18e99d8e4.html', {})
