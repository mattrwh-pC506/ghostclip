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
        return super().changeform_view(request, object_id, form_url, extra_context=ec)

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    pass

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'is_active', 'is_staff',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('is_active', 'is_staff', 'username', 'email', 'password', 'family',)

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('family', 'username', 'email',)
    search_fields = ('family', 'username', 'email',)
    ordering = ('family', 'username', 'email',)
    filter_horizontal = ()

admin.site.unregister(Group)
