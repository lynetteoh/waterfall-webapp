from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage

from .forms import SignUpForm, AvatarForm
from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, Transfer, GroupAccount

from datetime import datetime
import pytz

def index(request):
    return render(request, 'index.html')

def team(request):
    return render(request, 'team.html')

def product(request):
    return render(request, 'product.html')

@login_required
def viewMoreOp(request):
    title = "Outgoing Payments"
    user = str(request.user)
    outgoing = []

    if request.GET.get('query'):
        query = request.GET.get('query')
        context = collect_search_results(request.user, query)
        context["title"] = title
        context["user1"] = user
        context["key"] = "op"
        return render(request, 'view_more.html', context)

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

@login_required
def viewMoreIp(request):
    title = "Incoming Payments"
    user = str(request.user)
    incoming = []

    if request.GET.get('query'):
        query = request.GET.get('query')
        context = collect_search_results(request.user, query)
        context["title"] = title
        context["user1"] = user
        context["key"] = "ip"
        return render(request, 'view_more.html', context)

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

@login_required
def viewMoreH(request):
    title = "Transaction History"
    user = str(request.user)
    past = []

    if request.GET.get('query'):
        query = request.GET.get('query')
        context = collect_search_results(request.user, query)
        context["title"] = title
        context["user1"] = user
        context["key"] = "th"
        return render(request, 'view_more.html', context)

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
def group_dash(request, name):
    print("the name we got:", name)
    context = {"groupName": name}
    return render(request, 'group_dash.html', context)

@login_required
def dashboard(request):
    user_str = str(request.user)
    query = None if not request.GET.get('query') else request.GET.get('query')

    incoming, outgoing, past, requests, user_requests =\
        collect_dash_transfers(request.user, Transfer.objects.all(), query)
    context = {
        "past": past,
        "incoming" : incoming,
        "outgoing": outgoing,
        "user1": user_str,
        "requests": requests,
        "user_requests": user_requests,
    }
    if query:
        context["search"] = query
        return render(request, 'dashboard.html', context)

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
                                            collect_dash_transfers(request.user, Transfer.objects.all())
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
        # Update profile picture.
        if request.FILES:
            form = AvatarForm(request.POST, request.FILES)
            if form.is_valid():
                profile = user.profile
                profile.avatar = form.cleaned_data["avatar"]
                profile.save()
            else:
                context = {
                    "error": "The file you uploaded was either not an image or a corrupted image."
                }
                return render(request, 'profile.html', context)

        # Update profile details.
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
            tx = None
            if add_amount and float(add_amount) > 0:
                tx = user.account.deposit(float(add_amount))
            elif minus_amount and float(minus_amount) > 0:
                tx = user.account.withdraw(float(minus_amount))

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
            profile = Profile(user=user, avatar=None)
            profile.save()
            account = Account(user=user)
            account.save()
            login(request, user)
            return redirect('/dashboard')
    else:
        form = SignUpForm()
    return render(request, 'index.html', {'form': form})

@login_required
def pay(request):
    user = request.user
    all_users = User.objects.all()
    from_users = [user.username]
    user_groups = [g.name for g in user.profile.GroupAccount.all()]
    for g in user_groups:
        if g != user.username:
            from_users.append(g)

    pay_users = [g.name for g in GroupAccount.objects.all()]
    for u in all_users:
        if (u != user.username):
            pay_users.append(u.username)
    context = {
        "pay_page": "active",
        "user" : user,
        "user_groups": user_groups,
        "filter_users": pay_users,
        "from_users": from_users,
    }
    if request.method == "POST":
        try:
            from_acc = request.POST.get('pay_from')
            try:
                from_acc = User.objects.get(username=from_acc).account
            except:
                from_acc = GroupAccount.objects.get(name=from_acc).account
            if not from_acc:
                raise Exception("Invalid Transfer Account")

            payees = collect_recipients(request, 'pay_users')
            if not payees:
                raise Exception("Invalid Payees")

            subj = request.POST.get('pay_description')
            recurr = request.POST.get('pay_freq')
            date = request.POST.get('pay_date')
            amount = request.POST.get('pay_amount')

            for p in payees:
                try:
                    receiver = User.objects.get(username=p).account
                except:
                    receiver = GroupAccount.objects.get(name=p).account
                # Check for valid data.
                if not receiver or (receiver is from_acc):
                    raise Exception("Invalid TricklePay ID.")
                if not subj:
                    raise Exception("Empty Payment Description")
                if not amount or float(amount) < 0:
                    raise Exception("Invalid Payment Amount")
                if float(amount) > from_acc.balance:
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

                from_acc._create_transfer(receiver, subj, \
                                    float(amount), int(recurr), deadline, False)
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
    # all_users = User.objects.all().exclude(username=request.user.username)
    all_users = User.objects.all()
    from_users = []
    from_users.append(user.username)
    user_groups = user.profile.GroupAccount.all()

    from_users = [user.username]
    user_groups = [g.name for g in user.profile.GroupAccount.all()]
    for g in user_groups:
        if g != user.username:
            from_users.append(g)

    req_users = [g.name for g in GroupAccount.objects.all()]
    for u in all_users:
        if (u != user.username):
            req_users.append(u.username)
    context = {
        "request_page": "active",
        "user" : user,
        "user_groups": user_groups,
        "filter_users": req_users,
        "from_users": from_users,
    }
    if request.method == "POST":
        try:
            from_acc = request.POST.get('req_from')
            try:
                from_acc = User.objects.get(username=from_acc).account
            except:
                from_acc = GroupAccount.objects.get(name=from_acc).account
            if not from_acc:
                raise Exception("Invalid Request Account")

            requests = collect_recipients(request, 'req_users')
            if not requests:
                raise Exception("Invalid Request User")

            subj = request.POST.get('req_description')
            recurr = request.POST.get('req_freq')
            date = request.POST.get('req_date')

            for r in requests:
                amount = request.POST.get(r)
                try:
                    receiver = User.objects.get(username=r).account
                except:
                    print(r)
                    receiver = GroupAccount.objects.get(name=r).account
                    print("here")

                # Check for valid data.
                if not receiver or (receiver is from_acc):
                    raise Exception("Invalid TricklePay ID")
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

                transfer = from_acc._create_transfer(receiver, subj, \
                                    float(amount), int(recurr), deadline, True)
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
    all_users = User.objects.all().exclude(username=user.username)
    groups = []
    for g in user.profile.GroupAccount.all():
        groups.append(g.name)
    create_members = []
    for u in all_users:
        if (u != user.username):
            create_members.append(u.username)
    context ={
        "user" : user,
        "filter_members": create_members,
        "all_groups" :groups,
    }
    return render(request, 'create_group.html', context)

@login_required
def all_groups(request):
    user = request.user
    groups = [g for g in user.profile.GroupAccount.all()]
    context = {
        "user": user,
        "groups": groups,
    }
    if request.method == "POST":
        # Search requests.
        if request.POST.get("search-txt"):
            search = request.POST.get("search-txt")
            filtered_groups = []
            for g in groups:
                if search.lower() in g.name.lower():
                    filtered_groups.append(g)
                    continue
                for m in g.members.all():
                    if search.lower() in m.user.username.lower():
                        filtered_groups.append(g)
            context["search"] = search
            context["groups"] = filtered_groups

        # Manage group management.
        if request.POST.get("edit-group"):
            edit_group = request.POST.get("edit-group")
            if GroupAccount.objects.get(name=edit_group):
                return redirect('/group-management?g=' + edit_group)
    return render(request, 'all-groups.html', context)

@login_required
def group_management(request):
    user = request.user
    filter_users = [u.username for u in User.objects.all().exclude(username=user.username)]

    user_groups = []
    for g in user.profile.GroupAccount.all():
        user_groups.append(g.name)

    group = None
    if request.method == "GET" and request.GET.get("g"):
        edit_group = request.GET.get("g")
        group = GroupAccount.objects.get(name=edit_group)

    group_members = []
    if group:
        for p in group.members.all():
            if p.user != user:
                group_members.append(p.user.username)
    context = {
        "user" : user,
        "group" : group,
        "filter_members": filter_users,
        "user_groups:": user_groups,
        "group_members": group_members,
    }
    return render(request, 'group_management.html', context)

### HELPER FUNCTIONS ###

def transfer_has_query(t, query):
    if not query:
        return True
    q = query.lower()

    # Check user names for query.
    if (q in t.tx_from.title.lower()) or (q in t.tx_to.title.lower()):
        return True
    if t.tx_from.account.user and (q in t.tx_from.account.user.username.lower()):
        return True
    if t.tx_to.account.user and (q in t.tx_to.account.user.username.lower()):
        return True
    # Check group names for query.
    if not t.tx_from.account.user and (q in t.tx_from.account.groupaccount.name.lower()):
        return True
    if not t.tx_to.account.user and (q in t.tx_to.account.groupaccount.name.lower()):
        return True

    return False


def collect_dash_transfers(user, transfer_objects, query=None):
    incoming = []
    outgoing = []
    past = []
    requests = []
    user_requests = []

    for t in transfer_objects:
        # Check its a valid existing transfer relevant to current user.
        if t.is_deleted or not (t.tx_from.account == user.account or t.tx_to.account == user.account):
            continue

        # Check for search results.
        if not transfer_has_query(t, query):
            continue

        # Past transactions.
        if t.confirmed_at:
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

    incoming.sort(key=lambda x: x.deadline)
    outgoing.sort(key=lambda x: x.deadline)
    past.sort(key=lambda x: x.confirmed_at, reverse=True)
    requests.sort(key=lambda x: x.deadline)
    user_requests.sort(key=lambda x: x.deadline)

    # remove time from the format 
    for i in incoming:
        i.deadline = i.deadline.date()

    for i in outgoing:
        i.deadline = i.deadline.date()

    for i in past:
        i.confirmed_at = i.confirmed_at.date()

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
