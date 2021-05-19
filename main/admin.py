from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_no')

admin.site.register(User, UserAdmin)
