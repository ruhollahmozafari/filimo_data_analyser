from http.client import HTTPResponse
from django.shortcuts import render
from django.views.generic import ListView, DeleteView
from django.db.models import Q
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import DetailView
from urllib3 import Retry
from uni.settings import BASE_DIR
import os
from movie.models import *
from elasticsearch_dsl import Q as elastic_Q
from .documents import MovieDocument
from icecream import ic
from textblob import TextBlob
from googletrans import Translator, constants
translator = Translator()


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
    paginate_by = 500
    def get_queryset(self):
        query = self.request.GET.get('keywords', None)
        q = elastic_Q(
            'multi_match',
            query=query,
            fields=[
            'ename',
            'fname'])
        
        search = MovieDocument.search()[0:200].query(q)
        resp =  search.execute()
        ic(resp.hits.total)
        ic(len(resp.hits))
        return resp.hits

        # object_list = Movie.objects.filter(Q (ename__icontains=query) 
        # | Q(fname__icontains = query)).order_by('id')
        # return object_list



class MoviePageView(DetailView):


    model = Movie
    template_name = 'movie_page.html'
    context_object_name = 'movie'
    def get_polarity(self,movie):
        ic()
        result = {-1:0, -0.5 : 0 , 0:0, 0.5:0, 1:0}
        points = [-1, -0.5, 0, 0.5, 1 ]
        estring = ''
        for comment in movie.comment_movie.all(): 
            estring += comment.text + '@' # put all the commens text in one string to translate and separte them with @ 
        print('this is the ')
        translation = translator.translate(estring , dest ="en", src="fa")
        ecomments = translation.text.split('@')
        print('this is the len of ecommnte s',len(ecomments))
        print('this is the len of the movie comments',len(movie.comment_movie.all()))

        for indexer, comment in enumerate(movie.comment_movie.all()):
            comment_polarity = TextBlob(ecomments[indexer]).sentiment.polarity
            for indx in range(4):
                if  points[indx] < comment_polarity <= points[indx+1]:
                    result[points[indx+1]]+=1
                    break
            comment.polarity = comment_polarity
            comment.e_text = ecomments[indexer]
            comment.save()
            # ic()
            # ic(comment)
            # ic(comment_polarity)
            # ic('----------------------')
        # end of getting sentiment for each comment , now  get an average of them based on the number and like and dislike
        average_rating = sum([k*v for k,v in result.items()]) / sum([i for i in result.values()])
        movie.sentiment = int(round(average_rating, 3)*100)  # get a total average of sentiments 
        movie.sentiment_detail = result
        movie.save()
        return None

    def get_queryset(self):
        object_list = Movie.objects.filter(id = self.kwargs['pk'])
        return object_list
    
    def get(self, request , *args, **kwargs):
        movie = Movie.objects.get(id = kwargs['pk'])
        if  movie.sentiment == None:
            self.get_polarity(movie)
            ic('goin for the sentiment ')
        else:
            # self.get_polarity(movie)
            ic('passing the sentiment since it is full ')
            pass 
        return super().get(request, *args, **kwargs)




