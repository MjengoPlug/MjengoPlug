from django.contrib import admin
from .models import UserAccount
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class UserAdminConfig(UserAdmin):
    model = UserAccount
    search_fields = ('email', 'user_name', 'first_name',)
    list_filter = ('email', 'user_name', 'first_name', 'is_active', 'is_staff')
    ordering = ('user_name',)
    list_display = ('email', 'user_name', 'first_name', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'user_name', 'first_name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_name', 'first_name', 'password1', 'password2', 'is_active', 'is_staff')}
         ),
    )

admin.site.register(UserAccount, UserAdminConfig)
