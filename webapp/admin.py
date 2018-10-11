from django.contrib import admin
<<<<<<< HEAD
from webapp.models import Profile, Account, Transaction, Transfer, GroupAccount
=======
from webapp.models import Profile, Account, GroupAccount, Transaction, Transfer
>>>>>>> c9494fc093c2ad094abd1cd874cd731bbe6bc5be

admin.site.register(Profile)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Transfer)
admin.site.register(GroupAccount)
