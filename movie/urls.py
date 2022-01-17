from django.urls import path
from .views import *

app_name='movie' 
urlpatterns = [
    path("list/", ListMovie.as_view(), name = 'home'),
    path("", ListMovie.as_view(), name = 'home'),
    path('search_result/', SearchResultView.as_view(), name='search-results'),
    path('detail/<int:pk>/',MoviePageView.as_view(), name = 'movie_page' )
]
