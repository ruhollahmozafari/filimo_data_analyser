from django.shortcuts import render
from django.views.generic import ListView, DeleteView
from django.db.models import Q
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse, response
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from uni.settings import BASE_DIR
import os
from movie.models import *
from elasticsearch_dsl import Q as elastic_Q
from .documents import MovieDocument
# Create your views here.
class ListMovie(ListView):
    model = Movie
    template_name = 'main.html'
    context_object_name = 'movies'
    paginate_by = 18
    ordering = ('-id')
    
    # def get_context_data(self, **kwargs):
        # context = super(QuestionsInTags,self).get_context_data(**kwargs)
        # context["main_tag"]= self.tag
        # return context


class SearchResultView(ListView):

    model = Movie
    template_name = 'search_result.html'
    context_object_name = 'movies'
    def get_queryset(self):
        query = self.request.GET.get('keywords', None)
        q = elastic_Q(
            'multi_match',
            query=query,
            fields=[
                'fname',
                'ename',
            ])
        
        search = MovieDocument.search().query(q)
        resp =  search.execute()
        # object_list = Movie.objects.filter(Q (ename__icontains=self.keyword) 
        # | Q(fname__icontains = self.keyword)).order_by('id')
        
        print('resp is ',resp.hits)
        [print(type(hit)) for hit in resp.hits]
        return resp.hits

class MoviePageView(DetailView):

    model = Movie
    template_name = 'movie_page.html'
    context_object_name = 'movie'
    # lookup_field = 'pk'
    def get_queryset(self):
        object_list = Movie.objects.filter(id = self.kwargs['pk'])
        return object_list


