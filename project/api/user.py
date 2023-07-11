from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from project.api import check_auth, ADMIN_EMAIL
from project.model.user import User
from project.serializers import UserSerializer


class UserList(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        check_auth(request.META)

        users = User.objects.exclude(email=ADMIN_EMAIL)
        serializer = UserSerializer(users, many=True)
        content = {
            'result': 'ok',
            'contents': serializer.data
        }
        return Response(content)


class UserDetail(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, uuid):
        check_auth(request.META)

        try:
            user = User.objects.get(uuid=uuid)
            serializer = UserSerializer(user)
            content = {
                'result': 'ok',
                'contents': serializer.data
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {}
            }
            return Response(content)

    def put(self, request, uuid):
        check_auth(request.META)

        if enable := request.query_params.get("enable"):
            return self._update_user_enable(request, uuid, enable)
        return self._update_user(request, uuid)

    def _update_user_enable(self, request, uuid, enable):
        try:
            user = User.objects.get(uuid=uuid)
            user.enable = enable
            user.save()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {
                    "response": "user not found"
                }
            }
            return Response(content)

    def _update_user(self, request, uuid):
        try:
            user = User.objects.get(uuid=uuid)
            user.email = request.data["email"]
            if not request.META.get("HTTP_X_FEATURE_TYPE"):
                if user.pwd != request.data["pwd"]:
                    content = {
                        'result': 'nok',
                        'contents': {
                            "reason": "wrong password"
                        }
                    }
                    return Response(content)
                user.firstname = request.data["firstname"]
                user.lastname = request.data["lastname"]
                user.ip = request.data["ip"]
                user.summary = f'{user.email} {user.firstname} {user.lastname}'
                user.question1 = request.data["question1"]
                user.question2 = request.data["question2"]
                user.question3 = request.data["question3"]
            else:
                user.pwd = request.data["pwd"]
            user.save()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except KeyError:
            raise ValidationError("Invalid keys")
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {
                    "response": "user not found"
                }
            }
            return Response(content)

    def delete(self, request, uuid):
        check_auth(request.META)
        try:
            user = User.objects.filter(uuid=uuid)
            user.delete()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {}
            }
            return Response(content)


class UserEnable(APIView):
    renderer_classes = [JSONRenderer]

    def put(self, request, uuid, enable):
        check_auth(request.META)

        try:
            user = User.objects.get(uuid=uuid)
            user.enable = enable
            user.save()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {}
            }
            return Response(content)


class UserSearch(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, key):
        check_auth(request.META)

        try:
            # search by last name, first name, address, e-mail, or <contact identifier>
            user = User.objects.filter(Q(lastname=key) | Q(firstname=key) | Q(email=key) | Q(contact_id=key))
            serializer = UserSerializer(user)
            content = {
                'result': 'ok',
                'contents': serializer.data
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {}
            }
            return Response(content)