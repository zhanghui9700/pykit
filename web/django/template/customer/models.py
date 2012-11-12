#!/usr/bin/env python
#-*-coding=utf-8-*-

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)

    mobile = models.CharField(max_length=16)
