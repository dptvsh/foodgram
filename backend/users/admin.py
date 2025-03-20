from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import CustomUser, Follow


class FollowForm(forms.ModelForm):
    def clean(self):
        user = self.cleaned_data['user']
        following = self.cleaned_data['following']
        if user == following:
            raise forms.ValidationError(
                'Вы не можете подписаться на себя!',
            )


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'first_name', 'last_name',
    )
    search_fields = (
        'email', 'username',
    )
    empty_value_display = '-не задано-'
    exclude = ('password',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    form = FollowForm


admin.site.unregister(Group)
