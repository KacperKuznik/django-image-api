from django.contrib import admin
from .models import UserTier, User, Image
# Register your models here.

admin.site.register(UserTier)
admin.site.register(User)
admin.site.register(Image)
