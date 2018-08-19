from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.conf import settings
from django.conf import settings

import plaid

from main.models.user import User, Family
from main.models.item import Item
from main.models.transaction import Transaction, Account
from main.models.rules import RuleSet, NameRule, AmountRule, DateRule
from main.models.running_totals import RunningTotal

client = plaid.Client(client_id=settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET,
                      public_key=settings.PLAID_PUBLIC_KEY, environment=settings.PLAID_ENV)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    def changeform_view(self, request, object_id, form_url='', extra_context=None):
        ec = extra_context or {}
        ec['plaid_public_key'] = settings.PLAID_PUBLIC_KEY
        ec['plaid_environment'] = settings.PLAID_ENV

        if object_id:
            ci = Item.objects.get(pk=object_id)
            new_ptoken_response = client.Item.public_token.create(
                ci.access_token)
            public_token = new_ptoken_response['public_token']
            ec['plaid_item_public_token'] = public_token

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


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'mask', 'subtype',)


@admin.register(RuleSet)
class RuleSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'last_transaction_name',
                    'last_transaction_amount', 'predicted_next_transaction_date',)


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


@admin.register(RunningTotal)
class RunningTotaldmin(admin.ModelAdmin):
    list_display = ('amount', 'target', 'start_date', 'end_date',)
