from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, OneToOnePayment


def index(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }
    return render_to_response('index.html', context)

def dashboard(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }
    return render_to_response('dashboard.html', context)


def team(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }

    return render_to_response('team.html', context)

def profile(request):
        # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }
    return render_to_response('profile.html', context)

def balance(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }
    return render_to_response('balance.html', context)

def pay(request):
    all_users = User.objects.all().exclude(username='admin')
    users = all_users.exclude(username='admin')
    for user in users:
        print (user)
    context ={
        "users": users
    }
    return render(request, 'tricklepay.html', context)
