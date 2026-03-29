from django.test import TestCase

# Create your tests here.


from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer