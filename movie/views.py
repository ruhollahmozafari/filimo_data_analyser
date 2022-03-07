import time
from multiprocessing.dummy import Pool as ThreadPool
from .serializers import *
import requests
from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q
from django.views.decorators.http import require_POST, require_http_methods
from django.views.generic.detail import DetailView
import os
from movie.models import Movie
from elasticsearch_dsl import Q as elastic_Q
from .documents import MovieDocument
from icecream import ic
from textblob import TextBlob
import json
import emoji
from django.db.models.functions import Length


class Translation():
    """Handle translation using different api for a movie"""
    lang = 'en'
    action = 'google'
    token = '323029:621bbc1d8dfe02.87566886'
    rapid_api_key = '16cfd5816fmsh6528f260d31df4ep14e514jsn0d846d6f14f5'

    def comment_translator(self, movie):
        """after get the comment of a movie, translation process into a threatpool"""
        pool = ThreadPool(8)  # Threads
        n = 4  # sub list comment lenght
        # we create two list , one including comments with size of smaller than 120 and other bigger tham 
        all_comments = movie.comment_movie.all().annotate(
            text_len=Length("text")).filter(text_len__lt=120)#TODO: put the filter of non-translated
        sub_list_comment = [all_comments[i:i + n]for i in range(0, len(all_comments), n)]


        all_comments = movie.comment_movie.all()
        large_size_comment = all_comments.annotate(
            text_len=Length("text")).filter(text_len__gte=120,)#TODO put the filter of non-translated
        sub_list_comment += [[c] for c in large_size_comment]

        try:
            results = pool.map(self.translate_by_api, sub_list_comment)
            pass
        except Exception as e:
            raise e
        pool.close()
        pool.join()
        return True

    def translate_by_api(self,comments):
        """translate text of list of comment and save the translated part into db"""
            # if yes the size of the comment is not supported for microsoft api so use google 
        if len(comments) ==1 :
            print('going for the big comments\n\n') 
            comment = comments[0]
            query = comment.text
            url = f'https://one-api.ir/translate/?token={self.token}&action={self.action}&lang={self.lang}&q={query}'
            r = requests.get(url = url, timeout = 4 )
            comment.e_text = r.json().get('result')
            comment.save()
        # using microsoft api to translate 
        else:
            payload = [{'text': emoji.get_emoji_regexp().sub(u'', comment.text)}
                    for comment in comments]
            url = "https://microsoft-translator-text.p.rapidapi.com/translate"
            querystring = {"to": "en", "api-version": "3.0",
                        "profanityAction": "NoAction", "textType": "plain"}
            payload = json.dumps(payload)
            headers = {
                'content-type': "application/json",
                'x-rapidapi-host': "microsoft-translator-text.p.rapidapi.com",
                'x-rapidapi-key': self.rapid_api_key 
            }
            response = requests.request(
                "POST", url, data=payload, headers=headers, params=querystring, timeout = 4)

            for item, comment in zip(response.json(), comments):
                t = item.get("translations")[0]["text"]
                comment.e_text = t
                comment.save()
        return True


class Sentiment():
    points = [-1, -0.5, 0, 0.5, 1 ]
    sentiment_result = {-1:0, -0.5 : 0 , 0:0, 0.5:0, 1:0} # calculated number of

    def get_polarity(self,movie):# TODO put filter only on uncalculated comments

        comments = list(movie.comment_movie.all())

        pool = ThreadPool(8)  # Threads
        try:
            results = pool.map(self.get_sentiment_by_api, comments)
            pass
        except Exception as e:
            raise e
        pool.close()
        pool.join()
        average_rating = sum([k*v for k,v in self.sentiment_result.items()]) / sum([i for i in self.sentiment_result.values()])
        movie.sentiment = int(round(average_rating, 3)*100)  # get a total average of sentiments
        movie.sentiment_detail = self.sentiment_result
        movie.save()
        return None
    
    def get_sentiment_by_api(self, comment):
        """get polarity of the given comment with given """
        comment_polarity = TextBlob(comment.e_text).sentiment.polarity
        for indx in range(4):
            if  self.points[indx] < comment_polarity <= self.points[indx+1]:
                    self.sentiment_result[self.points[indx+1]]+=1
                    break
        comment.polarity = comment_polarity
        comment.save()


class MoviePageView(DetailView):

    model = Movie
    template_name = 'movie_page.html'
    context_object_name = 'movie'
    translation_class = Translation()
    sentiment_class = Sentiment()

    def get_queryset(self):
        object_list = Movie.objects.filter(id=self.kwargs['pk'])
        return object_list
    def get(self, request, *args, **kwargs):
        """if sentiment part is done just pass the data, else go for sentiment and then pass the data"""
        
        movie = Movie.objects.get(id=kwargs['pk'])

        # if the sentiment analysis has not done for this movie
        if not movie.sentiment:
            ic(f'translation and sentiment the movie {movie}')
            self.translation_class.comment_translator(movie = movie)        
            self.sentiment_class.get_polarity(movie)
            pass

        return super().get(request, *args, **kwargs)


# get numbers of comment into a excel file to read
        # cs = Comment.objects.all()[:200]
        # ser = CommentExcelSerializer(cs, many = True)
        # df = pd.DataFrame(ser.data)
        # df.to_excel('first 1000 comments.xlsx', encoding="UTF-8", index=False)

class ListMovie(ListView):
    model = Movie
    template_name = 'main.html'
    context_object_name = 'movies'
    paginate_by = 18
    ordering = ('-id')


class SearchResultView(ListView):

    model = Movie
    template_name = 'main.html'
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

        # search method in relational diagram
        # object_list = Movie.objects.filter(Q (ename__icontains=query)
        # | Q(fname__icontains = query)).order_by('id')
        # return object_list


        # get numbers of comment into a excel file to read
        # cs = Comment.objects.filter(polarity__isnull = False)
        # ser = CommentExcelSerializer(cs, many = True)
        # df = pd.DataFrame(ser.data)
        # df.to_excel('first 1000 comments.xlsx', encoding="UTF-8", index=False)

