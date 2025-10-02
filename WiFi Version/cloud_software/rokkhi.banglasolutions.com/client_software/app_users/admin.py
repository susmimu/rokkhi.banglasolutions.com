# ----------------------------------------------------------------------------------------------
from django.contrib import admin
from . models import Profile
# ----------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'email', 'city', 'country', 'acc_status', ]
    list_display_links = ['user', ]
    list_editable = ['acc_status', ]
    list_filter = ['acc_status', 'city', ]
    search_fields = ['user', 'phone_number', 'email', ]
    # ----------------------------------------------------------------------------------------------
    list_per_page = 15
    list_max_show_all = 15
    actions_on_top = True
    actions_on_bottom = True
# ----------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------
admin.site.register(Profile, ProfileAdmin)
# ----------------------------------------------------------------------------------------------
