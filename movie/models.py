from pydoc import resolve
from statistics import mode
from unittest import result
from django.db import models
from django.db.models.base import ModelState
from django.db.models.fields import TextField
from icecream import ic


class Genre(models.Model):#TODO load initial data later 
    fname = models.CharField(max_length=100, blank=True,
                             null=True, help_text='pesian name if exist')
    ename = models.CharField(max_length=100, blank=True,
                             null=True, help_text='english name if exist')
    def __str__(self) -> str:
        return self.fname
        
class Movie(models.Model):
    code = models.CharField(max_length= 50, blank= True, null= True, help_text= 'this the uniquer extracing from url for each movie')
    fname = models.CharField(max_length=500, blank=True,
                             null=True, help_text='pesian name if exist')
    ename = models.CharField(max_length=500, blank=True,
                             null=True, help_text='english name if exist')
    description = TextField(blank= True , null= True)
    summary = models.TextField(blank=True, null=True,)
    type = models.CharField(max_length=100, blank=True,
                            null=True, help_text='tvshow or movie')
    original_url = models.CharField(max_length=1000, blank=True, null=True, help_text= 'refer to filimo page', unique= True)
    release_date = models.DateField(blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank= True,)
    duration = models.DurationField(blank= True, null= True)
    image_url = models.CharField(max_length=1000, blank=True , null = True, help_text='url extract from filimo') 
    imdb_rating = models.FloatField(blank= True , null= True)  # TODO Check if rating must be based on filimo or imdb
    filimo_rating = models.FloatField(blank= True , null= True)  # TODO Check if rating must be based on filimo or imdb
    filimo_total_votes = models.BigIntegerField(blank= True , null= True)  # TODO Check if rating must be based on filimo or imdb
    sentiment = models.FloatField(blank= True , null= True, help_text= 'final number of sentiment analysis based on the comments')
    sentiment_detail = models.JSONField(blank= True, null= True, help_text='this is for the number of each point [-1, 0.5, 0. 0.5 , 1] based on the number of comments')
    # def overall_sentiment(self):
    #     result = {-1:0, -0.5 : 0 , 0:0, 0.5:0, 1:0}
    #     points = [-1, -0.5, 0, 0.5, 1 ]
    #     for c in self.comment_movie.all():
    #         for indexer in range(4):
    #             if  points[indexer] < c.polarity <= points[indexer+1]:
    #                 result[indexer+1]
    #                 ic()
    #                 break
    #         ic()
        
    #     return result

    # note : rate for tvshow are for all episode and seson not just one episode or season

    # fields that can ad later
    # casts
    # box_office
    # year # though have the release date
    # google and imdb rating
    def __str__(self) -> str:
        return f'{self.id} {self.ename}' if self.ename else self.fname
    def get_comments(self):
       comment_obj= self.comment_movie.all()
       comments = []
       for x in comment_obj:
           comments.append({'id': x.id, 'fname': x.fname, 'ename': x.ename})
       return comments
    def number_very_bad_comment(self):
        return self.sentiment_detail.get('-1',0)
    def number_bad_comment(self):
        return self.sentiment_detail.get('-0.5',0)
    def number_good_comment(self):
        return self.sentiment_detail.get('0.5',0)
    def number_very_good_comment(self):
        return self.sentiment_detail.get('1',0)
    def number_of_zero_comment(self):
        return self.sentiment_detail.get('0',0)
class Comment(models.Model):
    movie = models.ForeignKey(Movie, blank= True, null= True, on_delete=models.CASCADE, related_name='comment_movie')
    text = models.TextField(blank=True, null= True , max_length=1000)
    e_text = models.TextField(blank=True, null= True , max_length=1000, help_text='english translated version')
    date = models.CharField(blank=True, null=True, max_length=  100)
    vote_up = models.IntegerField(blank=True, null= True)
    vote_down = models.IntegerField(blank=True, null= True)
    polarity = models.FloatField(blank=True, null= True, help_text='this represent the sentiment analysis of this commnent -1 to 1 ')

    # start_testing = models.IntegerField(blank=True, null= True)
    def __str__(self) -> str:
        return str(self.id) + self.text[:100] if self.text else f'comment' 
