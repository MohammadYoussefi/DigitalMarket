from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserUpdateForm, UserCreationForm
from .models import User, OTPCode
from django.contrib.auth.models import Group


class UserAdmin(BaseUserAdmin):
    form = UserUpdateForm
    add_form = UserCreationForm

    list_display = ('email', 'full_name', 'phone_number', 'is_admin')
    list_filter = ('is_admin',)
    readonly_fields = ('last_login',)

    fieldsets = (
        ('Info', {'fields': ('email', 'phone_number', 'full_name', 'password')}),
    )

    add_fieldsets = (
        ('Add User', {'fields': ('email', 'phone_number', 'full_name', 'password1', 'password2')}),
    )

    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    filter_horizontal = ('user_permissions', 'groups')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at')  # Remove 'user' if it's here
    search_fields = ('phone_number',)
    list_filter = ('created_at',)
