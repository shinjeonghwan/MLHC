from django.shortcuts import render

def index(request):
    return render(request, "main_page/index.html")

def audio(request):
    return render(request, "main_page/audio.html")
