from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Messages)
class  messages(admin.ModelAdmin):
    list_display = ['id','sender','receiver','text','time_stamp']