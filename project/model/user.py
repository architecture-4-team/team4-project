import uuid as uuid
from django.db import models


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_id = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    pwd = models.CharField(max_length=64)
    firstname = models.CharField(max_length=32)
    lastname = models.CharField(max_length=32)
    ip = models.CharField(max_length=32)
    online = models.SmallIntegerField(default=1)
    enable = models.SmallIntegerField(default=1)
    summary = models.CharField(max_length=512)
    question1 = models.CharField(max_length=16)
    question2 = models.CharField(max_length=16)
    question3 = models.CharField(max_length=16)
    created_at = models.DateTimeField
    updated_at = models.DateTimeField

    class Meta:
        managed = False
        db_table = 'user_table'
