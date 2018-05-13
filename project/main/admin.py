from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf import settings

from .models import Family, User, Item, Calendar

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    pass

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        ec = extra_context or {}
        ec['plaid_public_key'] = settings.PLAID_PUBLIC_KEY
        ec['plaid_environment'] = settings.PLAID_ENV

        webhook_url = settings.WEBHOOK_BASE_URL
        if settings.APP_ENV != 'local':
            webhook_url += '/main/transactions_update'

        ec['transactions_webhook'] = webhook_url

        return super().changeform_view(request, object_id, form_url, extra_context=ec)

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    pass

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        exclude = ()

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    list_display = ('family', 'username', 'email',)
    search_fields = ('family', 'username', 'email',)
    ordering = ('family', 'username', 'email',)
    filter_horizontal = ()
    fieldsets = (
            (None, {'fields': ('family',)}),
            *BaseUserAdmin.fieldsets,
            )



    admin.site.unregister(Group)
