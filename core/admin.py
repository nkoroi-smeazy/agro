from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User, County, Ward, Locality, CommonInterestGroup, Farmer, Farm, FarmProduce

# Custom UserAdmin to include the user_type field
class CustomUserAdmin(BaseUserAdmin):
    # Extend the fieldsets to display the user_type
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),
    )

# Register the custom user model using our custom UserAdmin
admin.site.register(User, CustomUserAdmin)

# Register other models so they are accessible in the admin
admin.site.register(County)
admin.site.register(Ward)
admin.site.register(Locality)
admin.site.register(CommonInterestGroup)
admin.site.register(Farmer)
admin.site.register(Farm)
admin.site.register(FarmProduce)
