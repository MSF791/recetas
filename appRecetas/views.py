from django.shortcuts import render

def index(request):
    return render(request, 'index.html',)

def registrarse(request):
    return render(request, 'registrarse.html')