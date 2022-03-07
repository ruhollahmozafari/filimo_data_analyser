from django.contrib import admin
from jmespath import search

from user.views import MoviesList
from .models import *

class CommentInLine(admin.TabularInline):
    model = Comment

class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'fname', 'ename', 'sentiment')
    search_fields = ['id','fname', 'ename']
    ordering =('id', 'sentiment')
    # inlines = [CommentInLine, ]


# Register your models here.
admin.site.register(Movie,MovieAdmin)
admin.site.register(Genre)
admin.site.register(Comment)


