
# Script updates various transactions in the database.
# Will be called by the CronTab running in the background periodically.


from django.contrib.auth.models import User
from .models import Profile, Account, Transaction, OneToOnePayment

def update:
    print("Hello!")

# def pay(request):
    # # Temporary fixed user login
    # user = User.objects.filter(username='admin').distinct()[0]
    # all_users = User.objects.all().exclude(username='admin')
    #
    # if request.method == "POST":
    #     # Requires more extensive form validation
    #
    #     tx_sender = user.account._create_transaction(-10,'hi','w')
    #
    #     receiver_acc = User.objects.get(username=request.POST.get('pay_users')).account
    #     tx_receiver = receiver_acc._create_transaction(10,'hi','d')
    #
    #     link_tx = OneToOnePayment.objects.create(
    #         tx_from = tx_sender,
    #         tx_to = tx_receiver
    #     )
    #
    #     tx_sender.save()
    #     tx_receiver.save()
    #     link_tx.save()
    #
    #     return redirect('/dashboard')
