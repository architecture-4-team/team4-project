from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.exceptions import ParseError
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from project.models import User
from project.serializers import UserSerializer


# Create your views here.
class UserList(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        content = {'result': serializer.data}
        return Response(content)


class UserInfo(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, uuid):
        users = User.objects.filter(uuid=uuid)
        serializer = UserSerializer(users, many=True)
        content = {'result': serializer.data}
        return Response(content)


class Login(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        if not request.data:
            raise ParseError("No payload")

        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError("Invalid keys")

        users = User.objects.filter(uuid=username, pwd=password)
        if users:
            serializer = UserSerializer(users, many=True)
            content = {'result': serializer.data}
            return Response(content)
        else:
            content = {'result': ''}
            return Response(content)


class LoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(None, template_name='login.html')


class ContactsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(None, template_name='contacts.html')


class RegisterView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(None, template_name='register.html')


class UpdateView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(None, template_name='register.html')


class ResetView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request):
        return Response(None, template_name='reset.html')
