from django.contrib import admin
from webapp.models import Profile
from webapp.models import Account, Transaction
from webapp.models import Transfer

admin.site.register(Profile)

admin.site.register(Account)
admin.site.register(Transaction)

admin.site.register(Transfer)