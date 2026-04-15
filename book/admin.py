from django.contrib import admin


from .models import *

class AdminBooks(admin.ModelAdmin):
    list_display = ["title","author","description","rating","image_url","book_url"]


admin.site.register(Book,AdminBooks)