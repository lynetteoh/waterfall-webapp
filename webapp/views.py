from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404


def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')
