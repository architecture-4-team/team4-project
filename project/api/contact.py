from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from project.api import check_auth
from project.model.contact import Contact
from project.serializers import ContactSerializer


class ContactDetail(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, uuid):
        check_auth(request.META)

        favorite_uid = request.data.get("uuid")
        nickname = request.data.get("nickname")
        if not favorite_uid or not nickname:
            raise ParseError("Invalid payload")

        try:
            Contact.objects.get(favorite_uid=favorite_uid)
            content = {
                'result': 'nok',
                'contents': {
                    "response": "already exists"
                }
            }
            return Response(content)
        except ObjectDoesNotExist:
            contact = Contact(owner_uid=uuid, favorite_uid=favorite_uid, nickname=nickname)
            contact.save()
            content = {
                'result': 'ok',
                'contents': {}
            }
            return Response(content)
