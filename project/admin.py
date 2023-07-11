from django.contrib import admin
from project.model.user import User
from project.model.contact import Contact

# Register your models here.

# to set fields to display on admin page
class UserAdmin(admin.ModelAdmin):
	list_display = ("contact_id", "email", "firstname", "lastname", "enable")

class ContactAdmin(admin.ModelAdmin):
	list_display = ("nickname", "owner_uid", "favorite_uid")

admin.site.register(User, UserAdmin)
admin.site.register(Contact, ContactAdmin)