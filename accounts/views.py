from rest_framework.decorators import api_view, action
from rest_framework.response import Response 
from rest_framework import status, views, viewsets
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from accounts.models import User
from accounts.serializers import UserSerializer, ProfileSerializer


@api_view(['POST'])
def account_registration(request):
    user_data = request.data.get('user')
    if not user_data:
        return Response({"errors": {"body": ["User data must be provided."]}}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(data=user_data)
    serializer.is_valid(raise_exception=True)
    serializer.save()  
    return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def account_login(request):
    user_data = request.data.get('user')
    if not user_data:
        return Response({"errors": {"body": ["User data must be provided."]}}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(email=user_data.get('email'), password=user_data.get('password'))
    if user is not None:
        serializer = UserSerializer(user)
        jwt_token = RefreshToken.for_user(user)
        serializer_data = serializer.data
        serializer_data['token'] = str(jwt_token.access_token)
        return Response({"user": serializer_data}, status=status.HTTP_202_ACCEPTED)
    
    return Response({"errors": {"body": ["Invalid credentials."]}}, status=status.HTTP_400_BAD_REQUEST)


class UserView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, format=None, pk=None):
        user = request.user
        user_data = request.data.get('user')
        if not user_data:
            return Response({"errors": {"body": ["User data must be provided."]}}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(instance=user, data=user_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileDetailView(viewsets.ModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'delete']
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticatedOrReadOnly(),]
        return super().get_permissions()
    
    def list(self, request, username=None, *args, **kwargs):
        try: 
            profile = User.objects.get(username=username)
            serializer = self.get_serializer(profile)
            return Response({"profile": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"errors": {"body": ["Invalid User"]}}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, username=None, *args, **kwargs):
        profile = self.get_object()
        follower = request.user
        
        if profile == follower:
            return Response({"errors": {"body": ["Invalid follow Request"]}}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            profile.followers.add(follower)
            serializer = self.get_serializer(profile)
            return Response({"profile": serializer.data}, status=status.HTTP_200_OK)
            
        elif request.method == 'DELETE':
            if not profile.followers.filter(pk=follower.id).exists():
                return Response({"errors": {"body": ["Invalid unfollow Request"]}}, status=status.HTTP_400_BAD_REQUEST)
                
            profile.followers.remove(follower)
            serializer = self.get_serializer(profile)
            return Response({"profile": serializer.data}, status=status.HTTP_200_OK)
