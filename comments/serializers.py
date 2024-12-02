from rest_framework import serializers
from comments.models import Comment
from articles.serializers import AuthorSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(
        source='created', 
        format='%Y-%m-%dT%H:%M:%S.%fZ', 
        required=False
    )
    updated_at = serializers.DateTimeField(
        source='updated', 
        format='%Y-%m-%dT%H:%M:%S.%fZ', 
        required=False
    )
    body = serializers.CharField(source='content', required=True)

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'updated_at', 'body', 'author']

    def get_author(self, obj):
        request = self.context.get('request')
        return AuthorSerializer(obj.author, context={'request': request}).data

    def create(self, validated_data):
        user = self.context['request'].user
        article = self.context.get('article')
        if not article:
            raise serializers.ValidationError("Article context is required to create a comment.")
        
        return Comment.objects.create(
            **validated_data,
            author=user,
            article=article
        )
