from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from datetime import datetime

class Profile(models.Model):
    import pytz
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField()
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')
    # balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return '@{}'.format(self.user.username)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def register_deposit(self, title, value):
        return self._create_transaction(value, title, 'd')

    def _create_transaction(self, value, title, type):
        return Transaction.objects.create(
            account=self,
            title=title,
            value=value,
            transaction_type=type
        )

    def register_withdrawal(self, title, value):
        if self.balance >= value:
            return self._create_transaction(0-value, title, 'w')
        else:
            print('Account funds are insufficient.')
            return None

    def __str__(self):
        return '@{}'.format(self.user.username)

    # TODO: Change to utilize filter for confirmed_at field for ALL funcs below and exclude is_deleted
    @property
    def balance(self):
        return self.transaction_set.aggregate(Sum('value'))['value__sum']
    # TODO @jqhils below for profile page
    @property
    def num_payments(self):
        return 0
    @property
    def num_requests(self):
        return 0
    @property
    def num_groups(self):
        # TODO Change this after implementing groups
        return 0

class Transaction(models.Model):
    TRANSACTION_TYPES = {
        'withdrawal': 'w',
        'deposit': 'd',
    }

    TRANSACTION_TYPE_CHOICES = [
        (TRANSACTION_TYPES['withdrawal'], 'withdrawal'),
        (TRANSACTION_TYPES['deposit'], 'deposit'),
    ]

    title = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    transaction_type = models.CharField(
        max_length=1,
        default='d',
        choices=TRANSACTION_TYPE_CHOICES,
    )

    value = models.DecimalField(max_digits=10, decimal_places=4)
    is_deleted = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} | @{} | ${}'.format(self.created_at, self.account.user.username, self.value)

    def _copy(self):
        return Transaction.objects.create(
            account=self.account,
            title=self.title,
            value=self.value,
            transaction_type=self.type,
            is_pending=self.is_pending,
            created_at=self.created_at,
            modified_at=self.modified_at,
            confirmed_at=self.confirmed_at,
        )
        
class Transfer(models.Model):
    tx_from = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_from')
    tx_to = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_to')

    recurrence_days = models.IntegerField(blank=True, null=True)
    is_request = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    deadline = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{}-- ${} -->{}'.format(self.tx_from.account.user.username, self.tx_to.value, self.tx_to.account.user.username)

    def delete(self):
        # TODO check this works in multithreading models
        self.tx_from.is_deleted = True
        self.tx_to.is_deleted = True
        self.is_deleted = True
        self.tx_from.save()
        self.tx_to.save()
        self.save()

    def confirm_recurring(self, today):
        self.confirmed_at  = today
        self.save()
        self.tx_from.confirmed_at = today
        self.tx_from.is_pending   = False
        self.tx_from.save()
        self.tx_to.confirmed_at   = today
        self.tx_to.is_pending     = False
        self.tx_to.save()

        # Make a copy of this transaction if it is a recurring one.
        if (self.recurrence_days > 0):
            new_exec_date = today + timedelta(days=t.recurrence_days)
            tx_from_copy = self.tx_from._copy()
            tx_from_copy.created_at = today
            tx_from_copy.modified_at = today
            tx_from_copy.confirmed_at.null = True

            tx_to_copy = self.tx_to._copy()
            tx_to_copy.created_at = today
            tx_to_copy.modified_at = today
            tx_to_copy.confirmed_at.null = True

            Transfer.objects.create(
                tx_from=tx_from_copy,
                tx_to=tx_to_copy,
                deadline=new_exec_date,
                recurrence_days=self.recurrence_days,
                is_request=False,
            )
