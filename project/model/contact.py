import uuid
from django.db import models

from project.model.user import User


class Contact(models.Model):
    cid = models.PositiveIntegerField(primary_key=True)
    owner_uid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', db_column="owner_uid")
    favorite_uid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite', db_column="favorite_uid")
    nickname = models.CharField(max_length=32)
    created_at = models.DateTimeField
    updated_at = models.DateTimeField

    class Meta:
        managed = False
        db_table = 'contact_table'
        unique_together = (('owner_uid', 'favorite_uid'),)
