from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from comments.models import Comment
from comments.serializers import CommentSerializer
from articles.models import Article


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return super().get_permissions()

    def post(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        comment_data = request.data.get('comment', {})
        
        serializer_context = self.get_serializer_context()
        serializer_context['article'] = article
        
        serializer = self.get_serializer(data=comment_data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({"comment": serializer.data}, status=status.HTTP_201_CREATED)

    def list(self, request, slug, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        comments = Comment.objects.filter(article=article).order_by('-created')
        
        serializer = self.get_serializer(comments, many=True)
        return Response({"comments": serializer.data}, status=status.HTTP_200_OK)


class DeleteCommentView(generics.DestroyAPIView):

    def destroy(self, request, slug, id, *args, **kwargs):
        article = get_object_or_404(Article, slug=slug)
        comment = get_object_or_404(Comment, id=id)
        
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)
