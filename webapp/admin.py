from django.contrib import admin
from webapp.models import Profile, Account, Transaction, Transfer

admin.site.register(Profile)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Transfer)
