from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf import settings

from .models import (
    Family, User, Item, Transaction, Location, Category, Account,
    RuleSet, NameRule, AmountRule, DateRule)


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


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'date', 'name', 'pending',)
    ordering = ('date', 'pending',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('token',)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'mask', 'subtype',)


@admin.register(RuleSet)
class RuleSetAdmin(admin.ModelAdmin):
    list_display = ('item', 'name',)


@admin.register(NameRule)
class NameRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_set', 'operator', 'value',)


@admin.register(AmountRule)
class AmountRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_set', 'operator', 'value',)


@admin.register(DateRule)
class DateRuleAdmin(admin.ModelAdmin):
    list_display = (
        'rule_set',
        'repeats_every_num',
        'repeats_every_type',
        'starting_date',
        'day_range_buffer',
    )
