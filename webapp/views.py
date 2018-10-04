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
import pytz

def index(request):
    return render(request, 'index.html')

def team(request):
    return render(request, 'team.html')

def product(request):
    return render(request, 'product.html')


@ensure_csrf_cookie
def register_new(request):
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/dashboard')
    else:
        form = SignUpForm()
    return render(request, 'index.html', {'form': form})


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
                profile = Profile.objects.get(id=user.id)
                profile.avatar = form.cleaned_data["avatar"]
                profile.save()

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

@login_required
def pay(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    pay_users = []
    for u in all_users:
        if(u != user.username):
            pay_users.append(u.username)

    context = {
        "pay_page": "active",
        "user" : user,
        "filter_users": pay_users,
    }

    if request.method == "POST":
        try:
            print (request.POST)
            payees = [request.POST.get('pay_users0')]
            print (payees)

            if not payees:
                raise Exception("Invalid Payees.")

            for p in payees:
                print ("HERE + " + p)
                receiver = User.objects.get(username=p).account
                subj = request.POST.get('pay_description')
                amount = request.POST.get('pay_amount')
                recurr = request.POST.get('pay_freq')
                date = request.POST.get('pay_date')

                # Check for valid data.
                if not receiver or (receiver is user.account):
                    raise Exception("Invalid User.")
                if not subj:
                    raise Exception("Empty Payment Description")
                if not amount or float(amount) < 0:
                    raise Exception("Invalid Payment Amount")
                if float(amount) > user.account.balance:
                    raise Exception("Insufficient Funds")
                if recurr is None or int(recurr) < 0:
                    raise Exception("Invalid Payment Recurrence")
                if not date:
                    raise Exception("Invalid Payment Date")

                timezone = pytz.UTC
                today = timezone.localize(datetime.today()).date()
                deadline = \
                    timezone.localize(datetime.strptime(date, "%Y-%m-%d")).date() # yyyy-mm-dd
                if deadline < today:
                    raise Exception("Invalid Past Payment Date")

                print ("Creating transfer payment ")
                transfer = user.account._create_transfer(receiver, subj, float(amount), int(recurr), deadline, False)
                context['error'] = "Success"
        except Exception as e:
            print (e)
            context['error'] = str(e)
        finally:
            return render(request, 'tricklepay.html', context)
    # Regular pay view.
    return render(request, 'tricklepay.html', context)


def request_page(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    pay_users = []
    for u in all_users:
        if(u != user.username):
            pay_users.append(u.username)

    print("all_users ", all_users)
    context ={
        "request_page": "active",
        "user" : user,
        "filter_users": pay_users,

    }
    return render(request, 'request.html', context)
