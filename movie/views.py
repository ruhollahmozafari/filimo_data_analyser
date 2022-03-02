from google_trans_new import google_translator
import time
from multiprocessing.dummy import Pool as ThreadPool
from .serializers import *
import pandas as pd
import requests
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
import json
import emoji
from django.db.models.functions import Length
import datetime
action = 'google'
lang = 'en'

from functools import wraps
from time import process_time

translator = Translator()
token = '323029:621bbc1d8dfe02.87566886'



def comment_traslator(movie):
    pool = ThreadPool(40)  # Threads
    print('\n in the main comment handler \n')
    n = 4  # sub list comment lenght
    all_comments = movie.comment_movie.all().annotate(
        text_len=Length("text")).filter(text_len__lt=120)#TODO: put the filter of non-translated
    sub_list_comment = [all_comments[i:i + n]for i in range(0, len(all_comments), n)]

    # TODO: for big comments 
    all_comments = movie.comment_movie.all()
    large_size_comment = all_comments.annotate(
        text_len=Length("text")).filter(text_len__gte=120,)#TODO put the filter of non-translated
    sub_list_comment += [[c] for c in large_size_comment]

    try:
        results = pool.map(my_translator, sub_list_comment)
        pass
    except Exception as e:
        raise e
    pool.close()
    pool.join()
    time2 = time.time()
    return True

       
def my_translator(comments):
    print('\n ****** inside the my translator ****** \n')
        # if yes the size of the comment is not supported for microsoft api so use google 
    if len(comments) ==1 :
        print('going for the big comments\n\n') 
        comment = comments[0]
        query = comment.text
        url = f'https://one-api.ir/translate/?token={token}&action={action}&lang={lang}&q={query}'
        r = requests.get(url = url, timeout = 4 )
        comment.e_text = r.json().get('result')
        comment.save()
    # using microsoft data mining 
    else:
        payload = [{'text': emoji.get_emoji_regexp().sub(u'', comment.text)}
                for comment in comments]

        # send requests for microsoft translation 
        url = "https://microsoft-translator-text.p.rapidapi.com/translate"
        querystring = {"to": "en", "api-version": "3.0",
                    "profanityAction": "NoAction", "textType": "plain"}
        payload = json.dumps(payload)
        headers = {
            'content-type': "application/json",
            'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com",
            'x-rapidapi-key': "c10a3b3468mshea11bdae26f5911p1d9d13jsn108dd8377a12"
        }
        response = requests.request(
            "POST", url, data=payload, headers=headers, params=querystring)
        # e_comments = response.json()[0].get("translations")[0]["text"].split('@')
        # print('len of e comments :', len(e_comments))
        # return None
        for item, comment in zip(response.json(), comments):
            print('looooooooop for  comments')
            t = item.get("translations")[0]["text"]
            print('farsi comment', comment.text)
            print('english comment', t)

            comment.e_text = t
            comment.save()

    return True


def trans_eng(comment):
    lang = "en"
    t = google_translator(timeout=5)
    if comment.text in [None, '', ' ']:
        return None
    translate_text = t.translate(comment.text, lang)
    comment.e_text = translate_text
    Comment.save()
    return translate_text

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
        resp = search.execute()
        return resp.hits

        # object_list = Movie.objects.filter(Q (ename__icontains=query)
        # | Q(fname__icontains = query)).order_by('id')
        # return object_list


class MoviePageView(DetailView):

    model = Movie
    template_name = 'movie_page.html'
    context_object_name = 'movie'
    def get_polarity(self,movie):# TODO put filter only on uncalculated comments

        result = {-1:0, -0.5 : 0 , 0:0, 0.5:0, 1:0} # calculated number of
        points = [-1, -0.5, 0, 0.5, 1 ]
        

        for comment in movie.comment_movie.all():
            comment_polarity = TextBlob(comment.e_text).sentiment.polarity
            for indx in range(4):
                if  points[indx] < comment_polarity <= points[indx+1]:
                    result[points[indx+1]]+=1
                    break
            comment.polarity = comment_polarity
            comment.save()
        average_rating = sum([k*v for k,v in result.items()]) / sum([i for i in result.values()])
        movie.sentiment = int(round(average_rating, 3)*100)  # get a total average of sentiments
        movie.sentiment_detail = result
        movie.save()
        return None

    def get_queryset(self):
        object_list = Movie.objects.filter(id=self.kwargs['pk'])
        return object_list
    def get(self, request, *args, **kwargs):
        """if sentiment part is done just pass the data, else go for sentiment and then pass the data"""
        
        movie = Movie.objects.get(id=kwargs['pk'])
        t1 = datetime.datetime.now()
        
        # if the sentiment analysis has not done for this movie
        if not movie.sentiment:
            comment_traslator(movie)        
            self.get_polarity(movie)
        ic(datetime.datetime.now()- t1)

        return super().get(request, *args, **kwargs)


# get numbers of comment into a excel file to read
        # cs = Comment.objects.all()[:200]
        # ser = CommentExcelSerializer(cs, many = True)
        # df = pd.DataFrame(ser.data)
        # df.to_excel('first 1000 comments.xlsx', encoding="UTF-8", index=False)


