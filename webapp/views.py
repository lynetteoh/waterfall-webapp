from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404


def index(request):
    return render(request, 'index.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def profile(request):
    return render(request, 'profile.html')

def balance(request):
    return render(request, 'balance.html')

def pay(request):
    return render(request, 'pay1.html')

# def pay(request):
#     context = {"pay_page": "active"} 
#     return render(request, 'pay.html', context)

def request_payment(request):
    context = {"request_page": "active"} 
    return render(request, 'request.html', context)

def split(request):
    context = {"split_page": "active"} 
    return render(request, 'split.html', context)
    
