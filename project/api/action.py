from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import ParseError, AuthenticationFailed
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from project.api import check_auth
from project.model.user import User


class Register(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        if not request.data:
            raise ParseError("No payload")

        contact_id = None
        try:
            contact_id = request.data["contact_id"]
            User.objects.get(contact_id=contact_id)
            content = {
                'result': 'nok',
                'contents': {
                    "response": "contact id duplicated"
                }
            }
            return Response(content)
        except KeyError:
            raise ValidationError("Invalid keys")
        except ObjectDoesNotExist:
            email = request.data["email"]
            pwd = request.data["pwd"]
            firstname = request.data["firstname"]
            lastname = request.data["lastname"]
            ip = request.data["ip"]
            summary = f'{email} {firstname} {lastname}'
            question1 = request.data["question1"]
            question2 = request.data["question2"]
            question3 = request.data["question3"]

            user = User(contact_id=contact_id, email=email, pwd=pwd,
                        firstname=firstname, lastname=lastname, ip=ip, summary=summary,
                        question1=question1, question2=question2, question3=question3)
            user.save()
            content = {
                'result': 'ok',
                'contents': {
                    "response": user.uuid
                }
            }
            return Response(content)


class Login(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        if not request.data:
            raise ParseError("No payload")

        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            raise ParseError("Invalid keys")

        try:
            user = User.objects.get(email=email, pwd=password)
            # user.status = 1
            # user.save(update_fields=['status'])
            content = {
                'result': 'ok',
                'contents': {
                    'response': user.uuid
                }
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {}
            }
            return Response(content)


class LogOut(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request):
        uuid = check_auth(request.META)

        try:
            user = User.objects.get(uuid=uuid)
            # user.status = 0
            # user.save(update_fields=['status'])
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except ObjectDoesNotExist:
            raise AuthenticationFailed("Authorization failed")
