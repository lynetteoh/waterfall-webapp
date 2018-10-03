from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import SignUpForm

def index(request):
    return render(request, 'index.html')

def team(request):
    return render(request, 'team.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def profile(request):
    if request.method == "POST":
        user = request.user
        if request.POST.get('new_pic'):
            # Profile picture upload
            print("TODO upload")
            # user.profile.avatar = request.POST.get('new_pic')
        elif request.POST.get('first_name'):
            # Editing profile fields.
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            # Checking for password change.
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

@ensure_csrf_cookie
def register_new(request):
    if request.POST:
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        if user:
            user.save()
            account = Account(user = user)
            account.save()
            profile = Profile(user = user)
            profile.save()
            login(request, user)
            return redirect('/dashboard')
    else:
        return render(request, 'index.html')
          
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
            "pay_page": "active",
            "user" : user,
            "users": all_users,
        }
        return render(request, 'tricklepay.html', context)

def request_page(request):
    user = request.user 
    all_users = User.objects.all().exclude(username='admin')

    print("all_users ", all_users)
    context ={
        "request_page": "active",
        "user" : user,
        "users": all_users,
    }
    return render(request, 'request.html', context)

