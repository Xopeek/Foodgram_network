from django.contrib import admin

from .models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
    search_fields = (
        'username',
        'email'
    )


@admin.register(Subscribe)
class Subscribe(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author'
    )
    search_fields = (
        'user',
        'author'
    )
