from django.contrib import admin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'username', 'first_name', 'last_name',
    )
    search_fields = (
        'email', 'username',
    )
    empty_value_display = '-не задано-'


admin.site.register(Follow)
