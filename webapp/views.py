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

def viewMoreOp(request):
    title = "Outgoing Payments"
    user = str(request.user)
    outgoing = []

    transfers = Transfer.objects.all()
    for t in transfers:
        # Remove time from the date.
        # Outgoing or Incoming payments.
        tx_to = str(t.tx_to.account).strip("@")
        if tx_to != user and not t.is_request and not t.tx_from.confirmed_at:
            t.deadline = t.deadline.date()
            outgoing.append(t)

    context ={
        "title": title,
        "outgoing": outgoing,
        "user1": user,
        "key": "op",
    }

    return render(request, 'view_more.html', context)

def viewMoreIp(request):
    title = "Incoming Payments"
    user = str(request.user)
    incoming = []
    
    transfers = Transfer.objects.all()
    for t in transfers:
        # Remove time from the date.
        # Outgoing or Incoming payments.
        tx_to = str(t.tx_to.account).strip("@")
        if tx_to == user and not t.is_request and not t.tx_from.confirmed_at:
            t.deadline = t.deadline.date()
            incoming.append(t)


    context ={
        "title": title,
        "incoming": incoming,
        "user1": user,
        "key": "ip",
    }

    return render(request, 'view_more.html', context)

def viewMoreH(request):
    title = "Transaction History"
    user = str(request.user)
    past = []

    transfers = Transfer.objects.all()
    for t in transfers:
        if t.tx_from.confirmed_at:
            t.confirmed_at = t.confirmed_at.date()
            past.append(t)

    context ={
        "title": title,
        "past": past,
        "user1": user,
        "key": "th",
    }

    return render(request, 'view_more.html', context)



@login_required
def dashboard(request):
    user_str = str(request.user)
    incoming, outgoing, past, requests, user_requests = collect_dash_transfers(request.user)
    context = {
        "past": past,
        "incoming" : incoming,
        "outgoing": outgoing,
        "user1": user_str,
        "requests": requests,
        "user_requests": user_requests,
    }

    #if len(incoming) == 0:
     #   context['incoming'] = None
        
    print("outgoing is:", context['outgoing'])
            

    if request.method == "POST":
        transfer = request.POST.get('transfer')
        try:
            if request.POST.get('req') == "approve-req":
                context['error'] = request.user.account.approve_req(transfer)
            if request.POST.get('req') == "delete-req":
                context['error'] = request.user.account.delete_transfer(transfer)
        except Exception as e:
            context['error'] = str(e)
        finally:
            incoming, outgoing, past, requests, user_requests =\
                                            collect_dash_transfers(request.user)
            
            context['incoming'] = incoming
            context['outgoing'] = outgoing
            context['past'] = past
            context['requests'] = requests
            context['user_requests'] = user_requests

            if len(outgoing) == 0:
                context['outgoing'] = None
            
            return render(request, 'dashboard.html', context)
    return render(request, 'dashboard.html', context)

@login_required
def profile(request):
    if request.method == "POST":
        user = request.user
        if request.FILES:
            # get the posted form
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                profile = user.profile
                profile.avatar = form.cleaned_data["avatar"]
                profile.save()
            else:
                context = {
                    "error": "Upload a valid image. The file you uploaded was either not an image or a corrupted image."

                }
                return render(request, 'profile.html', context)


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
        except Exception as e:
            print(e)
            context['error'] = "Invalid Value"
        finally:
            return render(request, 'balance.html', context)

    return render(request, 'balance.html', context)

@ensure_csrf_cookie
def register_new(request):
    if request.POST:
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            profile = Profile()
            profile.user = user
            profile.avatar = None
            profile.save()
            account = Account()
            account.user = user
            account.save()
            login(request, user)
            return redirect('/dashboard')
    else:
        form = SignUpForm()
    return render(request, 'index.html', {'form': form})

@login_required
def pay(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    pay_users = []
    for u in all_users:
        if (u != user.username):
            pay_users.append(u.username)
    context = {
        "pay_page": "active",
        "user" : user,
        "filter_users": pay_users,
    }
    if request.method == "POST":
        try:
            payees = collect_recipients(request, 'pay_users')
            if not payees:
                raise Exception("Invalid Payees")

            subj = request.POST.get('pay_description')
            recurr = request.POST.get('pay_freq')
            date = request.POST.get('pay_date')
            amount = request.POST.get('pay_amount')

            for p in payees:
                receiver = User.objects.get(username=p).account
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

                timezone = pytz.timezone('Australia/Sydney')
                today = timezone.localize(datetime.today()).date()
                deadline = \
                    timezone.localize(datetime.strptime(date, "%Y-%m-%d")).date() # yyyy-mm-dd
    
                if deadline < today:
                    raise Exception("Invalid Past Payment Date")

                transfer = user.account._create_transfer(receiver, subj, float(amount), int(recurr), deadline, False)
                context['error'] = "Success"
        except Exception as e:
            print (e)
            context['error'] = str(e)
        finally:
            return render(request, 'pay.html', context)
    # Regular pay view.
    return render(request, 'pay.html', context)

@login_required
def request(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    req_users = []
    for u in all_users:
        if(u != user.username):
            req_users.append(u.username)
    context ={
        "request_page": "active",
        "user" : user,
        "filter_users": req_users,
    }
    if request.method == "POST":
        try:
            requests = collect_recipients(request, 'req_users')
            if not requests:
                raise Exception("Invalid Request User")

            subj = request.POST.get('req_description')
            recurr = request.POST.get('req_freq')
            date = request.POST.get('req_date')

            for r in requests:
                receiver = User.objects.get(username=r).account
                amount = request.POST.get(r)

                # Check for valid data.
                if not receiver or (receiver is user.account):
                    raise Exception("Invalid User.")
                if not subj:
                    raise Exception("Empty Payment Description")
                if not amount or float(amount) < 0:
                    raise Exception("Invalid Payment Amount")
                if recurr is None or int(recurr) < 0:
                    raise Exception("Invalid Payment Recurrence")
                if not date:
                    raise Exception("Invalid Payment Date")

                timezone = pytz.timezone('Australia/Sydney')
                today = timezone.localize(datetime.today()).date()
                deadline = \
                    timezone.localize(datetime.strptime(date, "%Y-%m-%d")).date() # yyyy-mm-dd
                if deadline < today:
                    raise Exception("Invalid Past Payment Date")

                transfer = user.account._create_transfer(receiver, subj, float(amount), int(recurr), deadline, True)
                context['error'] = "Success"
        except Exception as e:
            print (e)
            context['error'] = str(e)
        finally:
            return render(request, 'request.html', context)
    # Regular request view.
    return render(request, 'request.html', context)

@login_required
def create_group(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    create_members = []
    for u in all_users:
        if(u != user.username):
            create_members.append(u.username)
    context ={
        "user" : user,
        "filter_members": create_members,
    }
    return render(request, 'create_group.html', context)

@login_required
def group_management(request):
    user = request.user
    all_users = User.objects.all().exclude(username=request.user.username)
    manage_members = []
    for u in all_users:
        if(u != user.username):
            manage_members.append(u.username)
    context ={
        "user" : user,
        "filter_members": manage_members,
        "group_id": '1',
        "group_members": manage_members,
    }
    return render(request, 'group_management.html', context)

def collect_dash_transfers(user):
    incoming = []
    outgoing = []
    past = []
    requests = []
    user_requests = []

    for t in Transfer.objects.all():
        if t.is_deleted or not (t.tx_from.account == user.account or t.tx_to.account == user.account):
            continue

        # Remove time from the date.
        t.deadline = t.deadline.date()

        # Past transactions.
        if t.confirmed_at:
            t.confirmed_at = t.confirmed_at.date()
            past.append(t)
            continue
        # Pending or outgoing requests.
        if t.is_request:
            # Pending requests waiting for approval from user to transfer someone else.
            if t.tx_from.account == user.account:
                requests.append(t)
            else:
                user_requests.append(t)
            continue
        # Outgoing or Incoming payments.
        if t.tx_to.account == user.account:
            incoming.append(t)
        else:
            outgoing.append(t)

    past.reverse()
    return (incoming, outgoing, past, requests, user_requests)

# Collects payees for multi pay and multi requests.
def collect_recipients(request, user_type):
    # Collect all payees.
    payees = []
    i = 0
    r = request.POST.get(user_type + '0')
    while r:
        payees.append(r)
        i += 1
        r = request.POST.get(user_type + str(i))
    return payees
