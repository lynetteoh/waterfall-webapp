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
from django.contrib.auth.password_validation import validate_password

from datetime import datetime
import pytz, re

# Home landing page.
def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard')
    return render(request, 'index.html')

# Team description page.
def team(request):
    return render(request, 'team.html')

# Product description page.
def product(request):
    return render(request, 'product.html')

# New user registration page.
@ensure_csrf_cookie
def register_new(request):
    if request.POST:
        form = SignUpForm(request.POST)
        # Check validity of the registration form.
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

# Pending Transactions View more selection for main & group dashboard.
@login_required
def view_more_current(request, name=None):
    user = request.user
    acc = user.account
    title = "Pending Transactions"
    current = []
    group = None

    # View more for group accounts.
    if name and GroupAccount.objects.get(name=name):
        group = GroupAccount.objects.get(name=name)
        title += " - " + group.name
        acc = group.account

    # Get search queries and relevant transfers.
    query = None if not request.GET.get('query') else request.GET.get('query')
    (current, past) = collect_transfers(acc, Transfer.objects.all(), query)
    context = {
        "title": title,
        "current": current,
        "group": group,
        "acc" : acc,
    }
    # Search requests.
    if query:
        context["search"] = query
        return render(request, 'view_more.html', context)
    # User requests.
    if request.method == "POST":
        transfer = request.POST.get('transfer')
        try:
            if request.POST.get('req') == "approve-req":
                context['error'] = acc.approve_req(transfer)
            if request.POST.get('req') == "delete-req":
                context['error'] = acc.delete_transfer(transfer)
        except Exception as e:
            context['error'] = str(e)
        finally:
            current, past = collect_transfers(acc, Transfer.objects.all(), query)
            context['current'] = current
            return render(request, 'view_more.html', context)
    return render(request, 'view_more.html', context)

# Past Transactions complete selection for main/group dashboard.
@login_required
def view_more_history(request, name=None):
    user = request.user
    title = "Transaction History"
    group = None
    acc = user.account
    # View more for group accounts.
    if name and GroupAccount.objects.get(name=name):
        group = GroupAccount.objects.get(name=name)
        title += " - " + group.name
        acc = group.account
    # Gets search query and filter relevant transfers.
    query = None if not request.GET.get('query') else request.GET.get('query')
    (current, past) = collect_transfers(acc, Transfer.objects.all(), query)
    context = {
        "title": title,
        "past": past,
        "group": group,
        "acc" : acc,
    }
    # For search requests.
    if query:
        context["search"] = query
        return render(request, 'view_more.html', context)
    # Else display transfers.
    return render(request, 'view_more.html', context)

# User dashboard & landing page after login.
@login_required
def dashboard(request):
    user = request.user
    # Get search query and filter relevant transfers.
    query = None if not request.GET.get('query') else request.GET.get('query')
    current, past = collect_transfers(user.account, Transfer.objects.all(), query)
    tutorial = len(Transaction.objects.filter(account=user.account)) <= 0
    context = {
        "current" : current[:10],
        "past": past[:10],
        "user": user,
        "tutorial": tutorial,
    }
    # For search requests.
    if query:
        context["search"] = query
        return render(request, 'dashboard.html', context)
    # For user approval and cancellation of transfers.
    if request.method == "POST":
        transfer = request.POST.get('transfer')
        try:
            if request.POST.get('req') == "approve-req":
                context['error'] = user.account.approve_req(transfer)
            if request.POST.get('req') == "delete-req":
                context['error'] = user.account.delete_transfer(transfer)
        except Exception as e:
            context['error'] = str(e)
        finally:
            # Refresh on selected transfers.
            current, past = collect_transfers(user.account, Transfer.objects.all(), query)
            context['current'] = current[:10]
            context['past'] = past[:10]
            return render(request, 'dashboard.html', context)
    return render(request, 'dashboard.html', context)

# Profile settings page.
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

# Balance management page.
@login_required
def balance(request):
    user = request.user
    transactions = collect_transactions(user.account, Transaction.objects.all())
    context = {
        "user": user,
        "transactions": transactions,
    }
    if request.method == "POST":
        add_amount = request.POST.get('add_amount')
        minus_amount = request.POST.get('minus_amount')
        try:
            # Execute relevant user request and identify any errors.
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
            # Refresh on transactions relevant to users.
            transactions = collect_transactions(user.account, Transaction.objects.all())
            context["transactions"] = transactions
            return render(request, 'balance.html', context)
    return render(request, 'balance.html', context)

# Payment page.
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

    tutorial = len(Transfer.objects.all().filter(tx_from__account__user = user)) <= 0

    context = {
        "pay_page": "active",
        "user" : user,
        "user_groups": user_groups,
        "filter_users": pay_users,
        "from_users": from_users,
        "tutorial": tutorial,
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
            context['tutorial'] = False
            return render(request, 'pay.html', context)
    # Regular pay view.
    return render(request, 'pay.html', context)

# Request page.
@login_required
def request(request):
    user = request.user
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

    tutorial = len(Transfer.objects.all().filter(tx_to__account__user = user, is_request = True)) <= 0

    context = {
        "request_page": "active",
        "user" : user,
        "user_groups": user_groups,
        "filter_users": req_users,
        "from_users": from_users,
        "tutorial": tutorial,
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
            context['tutorial'] = False
            return render(request, 'request.html', context)
    # Regular request view.
    return render(request, 'request.html', context)

# New group creation page.
@login_required
def create_group(request):
    # get account owner
    user = request.user

    # get all user in the database except account owner
    create_members = [u.username for u in User.objects.all().exclude(username=user.username)]

    # context for frontend display
    context ={
        "user" : user,
        "filter_members": create_members,
    }

    # POST request
    if request.method == "POST":
        errors = []

        group_name = request.POST.get('group_name')
        # Group name must be between 1-30 characters.
        if group_name and (len(group_name) == 0 or len(group_name)) > 30:
            errors.append("The group name must be between 1-30 characters.")

        # Group name mustn't already exist as a group name or username
        if GroupAccount.objects.filter(name__iexact=group_name) or User.objects.filter(username__iexact=group_name):
            errors.append("This account name has been taken.")

        # Group name must only consist of alphanumeric + underscore chars
        if not bool(re.match(r'^[\w]+$', group_name)):
            errors.append("Account name must only consist of alphanumeric and underscore characters.")

        members = collect_recipients(request, 'members')
        # members must all exist.
        for m in members:
            if not User.objects.filter(username=m).exists():
                errors.append("A selected user does not exist.")

        # There must be no duplicates.
        if len(set(members)) != len(members):
            errors.append("A user is selected twice.")

        # if no error 
        if len(errors) == 0:
            # create group account with members and add it to database
            acc = Account.objects.create()
            gacc = GroupAccount.objects.create(account=acc, name=group_name)
            members = [User.objects.get(username=m).profile for m in members]
            gacc.members.set(members)

            acc.save()
            gacc.save()

            print("'{}' group created.".format(gacc))
            return redirect('/all-groups')

        else:
            # return error to front end for display
            context['errors'] = errors
            return render(request, 'create_group.html', context)

        return HttpResponse('success')

    else:
        return render(request, 'create_group.html', context)

# Groups page.
@login_required
def all_groups(request):
    # get account owner
    user = request.user

    # get all groups the account owner belongs
    groups = [g for g in user.profile.GroupAccount.all()]

    # context for frontend 
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

        # View group dashboard request.
        if request.POST.get("group-dash"):
            group_name = request.POST.get("group-dash")
            if GroupAccount.objects.get(name=group_name):
                return redirect('/group/' + group_name)

        # Edit group request.
        if request.POST.get("edit-group"):
            edit_group = request.POST.get("edit-group")
            if GroupAccount.objects.get(name=edit_group):
                return redirect('/edit-group?g=' + edit_group)
    return render(request, 'all-groups.html', context)


# Group dashboard page.
@login_required
def group_dash(request, name):
    # get account owner
    user = request.user

    # get groups
    try:
        group = GroupAccount.objects.get(name=name)
    except:
        group = None

    group_members = []

    # context for frontend
    context = {
        "user" : user,
        "group" : group,
        "group_members": group_members,
    }

    # get group members and pass it to frontend
    if group:
        for p in group.members.all():
            if p.user != user:
                group_members.append(p.user.username)
        current, past = collect_transfers(group.account, Transfer.objects.all())
        context["current"] = current[:10]
        context["past"] = past[:10]
        context["group_members"] = group_members

    if request.method == "POST":
        # Edit group request.
        if request.POST.get("edit-group"):
            edit_group = request.POST.get("edit-group")
            if GroupAccount.objects.get(name=edit_group):
                return redirect('/edit-group?g=' + edit_group)

        # Edit transfers request.
        if request.POST.get('transfer') and group:
            transfer = request.POST.get('transfer')
            try:
                if request.POST.get('req') == "approve-req":
                    context['error'] = group.account.approve_req(transfer)
                if request.POST.get('req') == "delete-req":
                    context['error'] = group.account.delete_transfer(transfer)
            except Exception as e:
                context['error'] = str(e)
            finally:
                current, past = collect_transfers(group.account, Transfer.objects.all())
                context['current'] = current[:10]
                context['past'] = past[:10]
                return render(request, 'group_dash.html', context)

        # Balance management request.
        add_amount = request.POST.get('add_amount')
        minus_amount = request.POST.get('minus_amount')
        try:
            tx = None
            if add_amount and float(add_amount) > 0:
                tx = group.account.deposit(float(add_amount), user.account)
            elif minus_amount and float(minus_amount) > 0:
                tx = group.account.withdraw(float(minus_amount), user.account)
            context['error'] = "Success" if tx else "Insufficient Funds"
        except Exception as e:
            context['error'] = e
        finally:
            current, past = collect_transfers(group.account, Transfer.objects.all())
            context['current'] = current[:10]
            context['past'] = past[:10]
            return render(request, 'group_dash.html', context)
    return render(request, 'group_dash.html', context)

# Edit group page.
@login_required
def edit_group(request):
    # get account owner
    user = request.user

    # get all user in the database except acc owner
    filter_users = [u.username for u in User.objects.all().exclude(username=user.username)]

    # get all groups name
    user_groups = []
    for g in user.profile.GroupAccount.all():
        user_groups.append(g.name)

    # get group info
    group = None
    if (request.method == "GET" and request.GET.get("g")) or (request.method == "POST" and request.GET.get("g")):
        edit_group = request.GET.get("g")
        group = GroupAccount.objects.get(name=edit_group)

    # add all members in a group 
    group_members = [user.username]
    if group:
        for p in group.members.all():
            if p.user.username != user.username:
                group_members.append(p.user.username)

    # context for frontend
    context = {
        "user" : user,
        "group" : group,
        "filter_members": filter_users,
        "user_groups:": user_groups,
        "group_members": group_members,
        "acc_owner": user.username
    }

    # POST request
    if request.method == "POST":
        errors = []
        leaveGroup = request.POST.get('leave_group')
        members = collect_recipients(request, 'members')

        # if user chose to leave group 
        if leaveGroup:
            # remove user from group members 
            group.members.remove(user.profile)
            group.save()
            # redirect to group list 
            return redirect('/all-groups')

        elif len(members):
            # Remove self
            members.remove(user.username)

            # List of members must not include self.
            if user.username in members:
                errors.append("List of members must not include self.")

            # Members must all exist.
            for m in members:
                if not User.objects.filter(username=m).exists():
                    errors.append("A selected user does not exist.")

            # There must be no duplicates.
            if len(set(members)) != len(members):
                errors.append("A user is selected twice.")

            # if no error, save changes for group
            if not len(errors):
                members = [user.username] + members
                members = [User.objects.get(username=m).profile for m in members]
                group.members.set(members)
                group.save()
                return redirect('/all-groups')

        # return error to frontend
        context['errors'] = errors
    return render(request, 'edit_group.html', context)

### HELPER FUNCTIONS ###

# Collects payees for multi pay and multi requests.
def collect_recipients(request, user_type):
    member_inputs = [m for m in list(request.POST) if bool(re.match(r'^{}[0-9]+$'.format(user_type), m))]
    recipients = [request.POST.get(m) for m in member_inputs]
    return recipients

# Checks if a particular transfer has query term in its name, description or involved users.
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


# Collects group transfers based on categories.
def collect_transfers(acc, transfer_objects, query=None):
    current = []
    past = []
    for t in transfer_objects:
        # Check its a valid existing transfer relevant to current user.
        if t.is_deleted or not (t.tx_from.account == acc \
                                or t.tx_to.account == acc):
            continue
        # Check for search results.
        if not transfer_has_query(t, query):
            continue
        # Past transactions.
        if t.confirmed_at:
            past.append(t)
            continue
        current.append(t)
    current.sort(key=lambda x: x.deadline)
    past.sort(key=lambda x: x.confirmed_at, reverse=True)

    # remove time for date-time format
    for i in current:
        i.deadline = i.deadline.date()
    for i in past:
        i.confirmed_at = i.confirmed.at.date()
    return (current, past)

# Collects group transfers based on categories.
def collect_transactions(acc, transactions, query=None):
    tx = []
    for t in transactions:
        # Check its a valid existing transfer relevant to current user.
        if t.is_deleted or not t.confirmed_at or not t.account == acc:
            continue
        if t.title == "Deposit" or t.title == "Withdrawal"\
            or t.title == "Deposit into Group"\
            or t.title == "Withdrawal from Group":
            tx.append(t)

    tx.sort(key=lambda x: x.confirmed_at, reverse=True)
    # remove time for date-time format
    for t in tx:
        t.confirmed_at = t.confirmed_at.date()
    return tx[:10]

# Collects group transfers based on categories.
def collect_transfers(acc, transfer_objects, query=None):
    current = []
    past = []
    for t in transfer_objects:
        # Check its a valid existing transfer relevant to current user.
        if t.is_deleted or not (t.tx_from.account == acc \
                                or t.tx_to.account == acc):
            continue
        # Check for search results.
        if not transfer_has_query(t, query):
            continue
        # Past transactions.
        if t.confirmed_at:
            past.append(t)
            continue
        current.append(t)
    current.sort(key=lambda x: x.deadline)
    past.sort(key=lambda x: x.confirmed_at, reverse=True)

    # remove time for date-time format
    for i in current:
        i.deadline = i.deadline.date()

    for i in past:
        i.confirmed_at = i.confirmed_at.date()

    return (current, past)

### DEPRECATED ###
# Collects transfers based on categories and given search query.
def collect_dash_transfers(acc, transfer_objects, query=None):
    incoming = []
    outgoing = []
    past = []
    requests = []
    user_requests = []

    for t in transfer_objects:
        # Check its a valid existing transfer relevant to current user.
        if t.is_deleted or not (t.tx_from.account == acc or t.tx_to.account == acc):
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
            if t.tx_from.account == acc:
                requests.append(t)
            else:
                user_requests.append(t)
            continue
        # Outgoing or Incoming payments.
        if t.tx_to.account == acc:
            incoming.append(t)
        else:
            outgoing.append(t)

    incoming.sort(key=lambda x: x.deadline)
    outgoing.sort(key=lambda x: x.deadline)
    past.sort(key=lambda x: x.confirmed_at, reverse=True)
    requests.sort(key=lambda x: x.deadline)
    user_requests.sort(key=lambda x: x.deadline)

    # remove time for date-time format
    for i in incoming:
        i.deadline = i.deadline.date()

    for i in outgoing:
        i.deadline = i.deadline.date()

    for i in past:
        i.confirmed_at = i.confirmed_at.date()

    return (incoming, outgoing, past, requests, user_requests)
