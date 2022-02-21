
class MovieDocument():
    pass
class CommentDocument():
    pass
# from django_elasticsearch_dsl import Document, fields
# from django_elasticsearch_dsl.registries import registry
# from elasticsearch_dsl import field
# from .models import Movie, Comment, Genre
# @registry.register_document
# class MovieDocument(Document):
#     genres = fields.NestedField(properties={
#         'id': fields.IntegerField(),
#         'fname': fields.TextField(),
#         'ename': fields.TextField()
#     })
#     class Index:
#         name = 'movies'
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}
#     class Django:
#         model = Movie # The model associated with this Document

#         fields = [
#             'id',
#             'code',
#             'original_url',
#             'fname',
#             'ename',
#             'summary',
#             'description',
#             'imdb_rating',
#             'filimo_rating',
#             'filimo_total_votes',
#             'image_url']


# @registry.register_document
# class CommentDocument(Document):
#     # movie = fields.ObjectField(properties={
#     #     'id': fields.IntegerField(),
#     #     'ename': fields.TextField(),
#     #     'fname': fields.TextField(),
#     # })
#     class Index:
#         # Name of the Elasticsearch index
#         name = 'comments'
#         # See Elasticsearch Indices API reference for available settings
#         settings = {'number_of_shards': 1,
#                     'number_of_replicas': 0}

#     class Django:
#         model = Comment # The model associated with this Document

#         fields = [
#             'id',
#             'text',
#             'vote_up',
#             'vote_down',
#         ]
#     # def prepare(self, instance):
#     #     return instance.get_comments()


