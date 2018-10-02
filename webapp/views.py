from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import SignUpForm

def index(request):
    # Temporary fixed user login
    user = User.objects.filter(username='admin').distinct()[0]
    context = {
        "user": user
        }
    return render_to_response('index.html', context)
    # if request.method == 'POST':
    #     username = request.POST.get('username')
    #     email = request.POST.get('email')
    #     password = request.POST.get('password')
    #     user = User.objects.create_user(username=username, email=email, password=password)
    #     user.save()
    #     login(request, user)
    #     return redirect('/dashboard')

    # return render(request, 'index.html')

def team(request):
    return render(request, 'team.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        new_pass = request.POST.get('password')
        if new_pass:
            user.set_password(new_pass)
            user.save()
    return render(request, 'profile.html')

@login_required
def balance(request):
    user = request.user

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

@login_required
def pay(request):
    user = request.user
    all_users = User.objects.all().exclude(username='admin')

    if request.method == "POST":
        # Requires more extensive form validation

        tx_sender = user.account._create_transaction(-10,'hi','w')

        receiver_acc = User.objects.get(username=request.POST.get('pay_users')).account
        tx_receiver = receiver_acc._create_transaction(10,'hi','d')

        link_tx = Transfer.objects.create(
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
