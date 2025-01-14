from django.http import HttpResponse
from django.shortcuts import render
# Class-based view

def home(request):
        return render(request, 'index.html')
