from django.contrib import admin
from .models import CustomUser as User, Address, Profile


admin.site.register(Address)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]



