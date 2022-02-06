from django.contrib import admin
from jmespath import search

from user.views import MoviesList
from .models import *


class MovieAdmin(admin.ModelAdmin):
    search_fiels = ("id", "fname", "ename")
    list_display = ('id', 'fname', 'ename', )


# Register your models here.
admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
admin.site.register(Comment)


