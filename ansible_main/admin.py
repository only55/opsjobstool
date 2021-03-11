from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Role)
admin.site.register(RoleCommand)
admin.site.register(Command)
