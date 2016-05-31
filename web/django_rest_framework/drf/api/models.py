from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    mobile = models.CharField(max_length=32, null=True, blank=True)


class BaseModel(models.Model):
    deleted = models.BooleanField(default=False)
    create_date = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        abstract = True
    

class CloudBaseModel(BaseModel):
    user = models.ForeignKey(User, null=True, blank=True)
    meta = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
    

class Image(CloudBaseModel):
    name = models.CharField(_('Name'), max_length=128)

    class Meta:
        db_table = "cloud_image"


class Keypair(CloudBaseModel):
    name = models.CharField(_('Name'), max_length=128)

    class Meta:
        db_table = "cloud_keypair"


class Network(CloudBaseModel):
    name = models.CharField(_('Name'), max_length=128)
    
    class Meta:
        db_table = "cloud_network"


class Instance(CloudBaseModel):
    name = models.CharField(_('Name'), max_length=128)
    image = models.ForeignKey("api.Image", related_name="used_instances")
    keypair = models.ForeignKey("api.Keypair", related_name="used_instances",  null=True, blank=True)
    networks = models.ManyToManyField("api.Network", blank=True)

    class Meta:
        db_table = "cloud_instance"


