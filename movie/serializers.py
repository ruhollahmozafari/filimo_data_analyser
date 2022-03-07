# from rest_framewor
from rest_framework.serializers import ModelSerializer
from .models import Comment, Movie

class CommentExcelSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"



