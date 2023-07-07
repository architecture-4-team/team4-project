from rest_framework import serializers

from project.model.contact import Contact
from project.model.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('pwd', 'summary')


class ContactSerializer(serializers.ModelSerializer):
    favorite_uid = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ('favorite_uid', 'nickname')
