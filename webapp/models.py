from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User


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
            return self._create_transaction(value, title, 'w')
        else:
            print('Account funds are insufficient.')
            return None

    # TODO: Change to utilize filter for confirmed_at field.
    @property
    def balance(self):
        return self.transaction_set.aggregate(Sum('value'))['value__sum']

    def __str__(self):
        return '@{}'.format(self.user.username)

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

    is_pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)



    def __str__(self):
        return '{} | @{} | ${}'.format(self.created_at, self.account.user.username, self.value)

class Transfer(models.Model):
    tx_from = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_from')
    tx_to = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='tx_to')

    recurrence_days = models.IntegerField(blank=True, null=True)
    is_request = models.BooleanField(default=False)
    
    deadline = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{}-- ${} -->{}'.format(self.tx_from.account.user.username, self.tx_to.value, self.tx_to.account.user.username)
