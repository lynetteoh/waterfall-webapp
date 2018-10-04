from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404

from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import SignUpForm, AvatarForm

from django.core.files.storage import FileSystemStorage

from datetime import datetime

def index(request):
    return render(request, 'index.html')

def team(request):
    return render(request, 'team.html')

def product(request):
    return render(request, 'product.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def profile(request):

    if request.method == "POST":
        user = request.user

        if request.FILES:
            # get the posted form
            form = AvatarForm(request.POST, request.FILES)

            if form.is_valid():
                print("form is valid")
                profile = Profile.objects.get(id=user.id)
                profile.avatar = form.cleaned_data["avatar"]
                profile.save()
            else:
                print("form is invalid")
                print(form.errors)

        if request.POST.get('first_name'):
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
    else:
        form = AvatarForm()

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
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            account = Account(user = user)
            account.save()
            profile = Profile(user = user)
            profile.avatar = None
            profile.save()
            login(request, user)
            return redirect('/dashboard')
        except:
            return render(request, 'index.html')
    return render(request, 'index.html')

@login_required
def pay(request):
    user = request.user
    all_users = User.objects.all().exclude(username=user.username)

    if request.method == "POST":
        try:
            receiver = User.objects.get(username=request.POST.get('pay_users')).account
            subj = request.POST.get('pay_description')
            amount = request.POST.get('pay_amount')
            recurr = request.POST.get('pay_freq')
            date = request.POST.get('pay_date')
            if not receiver or (receiver is user.account):
                context['error'] = "Invalid User."
            elif not subj:
                context['error'] = "Empty Payment Description"
            elif not amount or float(amount) < 0:
                context['error'] = "Invalid Payment Amount"
            elif float(amount) <= receiver.balance:
                context['error'] = "Insufficient Funds"
            elif recurr is None or int(recurr) < 0:
                context['error'] = "Invalid Payment Recurrence"
            elif not date:
                context['error'] = "Invalid Dates"
            else:
                print ("Creating transfer payment ")
                deadline = datetime.strptime(date, "%Y %m %d") # yyyy-mm-dd
                print (" for deadline ")
                print (deadline)
                transfer = Transaction._create_transfer(user.account, receiver, subj, float(amount), int(recurr), deadline, False)
                context['error'] = "Success"
        except:
            context['error'] = "Invalid Payment Request."
        finally:
            context ={
                "pay_page": "active",
                "user" : user,
                "users": all_users,
            }
            return render(request, 'tricklepay.html', context)
    # Regular pay view.
    context = {
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
