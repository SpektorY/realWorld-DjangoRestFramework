from rest_framework import generics, status, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response 

from comments.models import Comment
from comments.serializers import CommentSerializer
from articles.models import Article


class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer 
    permission_classes=[IsAuthenticated,]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return super().get_permissions()

    def post(self, request, slug, *args, **kwargs):
        try:
            article = Article.objects.get(slug=slug)
            comment_data = request.data.get('comment')
            
            serializer_context = self.get_serializer_context()
            serializer_context['article'] = article
            
            serializer = self.get_serializer(data=comment_data, context=serializer_context)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        
            return Response({ "comment": serializer.data } ,status=status.HTTP_201_CREATED)
            
        except Article.DoesNotExist:
            return Response({"errors": {"body": ["Article not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": {"body": ["Bad Request", str(e)]}}, status=status.HTTP_400_BAD_REQUEST)
            
    def list(self, request, slug, *args, **kwargs):
        try:
            article = Article.objects.get(slug=slug)
            comments = Comment.objects.filter(article=article).order_by('-created')
            serializer = self.get_serializer(comments, many=True)
            response = {'comments': serializer.data}
            return Response(response, status=status.HTTP_200_OK)
            
        except Article.DoesNotExist:
            return Response({"errors": {"body": ["Article not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": {"body": ["Bad Request", str(e)]}}, status=status.HTTP_400_BAD_REQUEST)


class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def destroy(self, request, slug, id, *args, **kwargs):
        try:
            article = Article.objects.get(slug=slug)
            comment = Comment.objects.get(id=id)
            if comment.author != request.user:
                return Response({"errors": {"body": ["You do not have permission to delete this comment."]}}, 
                                status=status.HTTP_403_FORBIDDEN)
            self.perform_destroy(comment)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Article.DoesNotExist:
            return Response({"errors": {"body": ["Article not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"errors": {"body": ["Comment not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": {"body": ["Bad Request", str(e)]}}, status=status.HTTP_400_BAD_REQUEST)


class LikeCommentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slug, id, *args, **kwargs):
        try:
            article = Article.objects.get(slug=slug)
            comment = Comment.objects.get(id=id, article=article)
            if request.user in comment.likes.all():
                return Response({"errors": {"body": ["You already liked this comment."]}}, 
                                status=status.HTTP_400_BAD_REQUEST)
            comment.likes.add(request.user)
            return Response({"message": "Comment liked successfully."}, status=status.HTTP_200_OK)
        
        except Article.DoesNotExist:
            return Response({"errors": {"body": ["Article not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"errors": {"body": ["Comment not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": {"body": ["Bad Request", str(e)]}}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, slug, id, *args, **kwargs):
        try:
            article = Article.objects.get(slug=slug)
            comment = Comment.objects.get(id=id, article=article)
            if request.user not in comment.likes.all():
                return Response({"errors": {"body": ["You have not liked this comment."]}}, 
                                status=status.HTTP_400_BAD_REQUEST)
            comment.likes.remove(request.user)
            return Response({"message": "Comment unliked successfully."}, status=status.HTTP_200_OK)
        
        except Article.DoesNotExist:
            return Response({"errors": {"body": ["Article not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Comment.DoesNotExist:
            return Response({"errors": {"body": ["Comment not found."]}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"errors": {"body": ["Bad Request", str(e)]}}, status=status.HTTP_400_BAD_REQUEST)
