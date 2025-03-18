from django.contrib import admin
from .models import CustomUser as User, Address, Profile


class AddressInline(admin.StackedInline):
    model = Address
    can_delete = False
    verbose_name_plural = 'Address'

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline, AddressInline]




