from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer

# TODO:
# * Handle User sessions instead of hard code
# * User session authentication

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

    if request.method == "POST":
        add_amount = request.POST.get('add_amount')
        minus_amount = request.POST.get('minus_amount')

        try:
            if add_amount and float(add_amount) > 0:
                tx = user.account.register_deposit("Deposit", float(add_amount))
                tx.save()
                context['error'] = "Success"
            elif minus_amount and float(minus_amount) > 0:
                tx = user.account.register_withdrawal("Withdrawal", float(minus_amount))
                if not tx:
                    context['error'] = "Insufficient Funds"
                else:
                    tx.save()
                    context['error'] = "Success"
        except:
            context['error'] = "Invalid Value"
        finally:
            return render(request, 'balance.html', context)

    return render(request, 'balance.html', context)

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
