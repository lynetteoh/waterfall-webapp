from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext


# TODO:
# * Handle User sessions instead of hard code
# * User session authentication

def index(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]

    context = {
        "user": user
        }
    return render(request, 'index.html', context)

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

def login(request):
    return render_to_response('login.html')

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

@ensure_csrf_cookie
def register_new(request):
    if request.POST:
        #DO VALIDATION HERE, AND IF USER IS ADDED TO DB GO TO SUCCESS PAGE
        username = request.POST['username']
        #pw = request.POST['password'] #PROBS NEED TO HASH THIS and STORE in DB
        email = request.POST['email']
        print("The username is:", username)

        return render(request, "register_success.html")

        #CAN DO AN IF STATEMENT TO REDIRECT TO HOME PAGE IF FAILED
        #return redirect('/')
        
    return render(request, "register_success.html.html")

def pay(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]
    all_users = User.objects.all().exclude(username='admin')

    if request.method == "POST":
        # Requires more extensive form validation

        tx_sender = user.account._create_transaction(-10,'hi','w')

        receiver_acc = User.objects.get(username=request.POST.get('pay_users')).account
        tx_receiver = receiver_acc._create_transaction(10,'hi','d')

        link_tx = OneToOnePayment.objects.create(
            tx_from = tx_sender,
            tx_to = tx_receiver
        )

        tx_sender.save()
        tx_receiver.save()
        link_tx.save()

        return redirect('/dashboard')

    else:
        pass
        context ={
            "user" : user,
            "users": all_users,
        }
        return render(request, 'tricklepay.html', context)
