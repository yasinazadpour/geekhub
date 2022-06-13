from django.contrib import admin
from accounts.models import MyUser
from django.utils.translation import gettext_lazy as _



@admin.register(MyUser)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('image', 'name', 'email',)}),
        (_('Permissions'), {
             'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
         }),
         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
     )

    list_display = ('username', 'name', 'email', 'is_staff','is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'name', 'email')
