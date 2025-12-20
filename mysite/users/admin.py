from django.contrib import admin
from .models import UserProfile, Address

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('profile', 'city', 'state', 'is_default')
    list_filter = ('is_default', 'state')
