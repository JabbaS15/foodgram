from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


@register(CustomUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'email',
    )
    fields = (
        ('username', 'email', ),
        ('first_name', 'last_name', 'password'),
        ('is_subscribed', )
    )
    fieldsets = []

    search_fields = (
        'username', 'email',
    )
    list_filter = (
        'first_name', 'email',
    )
    save_on_top = True
