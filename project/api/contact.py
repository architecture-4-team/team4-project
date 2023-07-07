from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from project.api import check_auth
from project.model.contact import Contact
from project.model.user import User
from project.serializers import ContactSerializer


class ContactDetail(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, uuid):
        check_auth(request.META)

        favorite_uid = request.data.get("favorite_uuid")
        nickname = request.data.get("nickname")
        if not favorite_uid or not nickname:
            raise ParseError("Invalid payload")

        try:
            Contact.objects.get(owner_uid=uuid, favorite_uid=favorite_uid)
            content = {
                'result': 'nok',
                'contents': {
                    "response": "already exists"
                }
            }
            return Response(content)
        except ObjectDoesNotExist:
            try:
                owner = User.objects.get(uuid=uuid)
                favorite = User.objects.get(uuid=favorite_uid)
                contact = Contact(owner_uid=owner, favorite_uid=favorite, nickname=nickname)
                contact.save()
                content = {
                    'result': 'ok',
                    'contents': {}
                }
                return Response(content)
            except ObjectDoesNotExist:
                raise ValidationError("can not find favorite in user")

    def get(self, request, uuid):
        check_auth(request.META)

        context = {
            'exclude_fields': [
                'cid'
            ]
        }

        contacts = Contact.objects.filter(owner_uid=uuid)
        if contacts:
            serializer = ContactSerializer(contacts, many=True, context=context)
            content = {
                'result': 'ok',
                'contents': serializer.data
            }
            return Response(content)
        else:
            content = {
                'result': 'ok',
                'contents': {}
            }
        return Response(content)

    def delete(self, request, uuid):
        check_auth(request.META)

        favorite_uid = request.data.get("uuid")
        if not favorite_uid:
            raise ParseError("Invalid payload")

        try:
            contact = Contact.objects.get(owner_uid=uuid, favorite_uid=favorite_uid)
            contact.delete()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
        except ObjectDoesNotExist:
            content = {
                'result': 'nok',
                'contents': {
                    "response": "contact not found"
                }
            }
            return Response(content)
