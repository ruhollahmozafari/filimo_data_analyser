from django.contrib import admin

from user.views import MoviesList
from .models import *
# Register your models here.
admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Comment)