from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.
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
