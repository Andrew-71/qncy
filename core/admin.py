from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import *

# Enormous crutch just to save profile pictures
class CustomUserAdmin(UserAdmin):
    fieldsets = tuple(
        (fieldset[0], {
            **{key: value for (key, value) in fieldset[1].items() if key != 'fields'},
            'fields': fieldset[1]['fields'] + ('pfp',)
        })
        if fieldset[0] == 'Personal info'
        else fieldset
        for fieldset in UserAdmin.fieldsets
    )

admin.site.register(User, CustomUserAdmin)
