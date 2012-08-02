#coding=utf-8
#cash register
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Item(models.Model):
    user = models.ForeignKey(User,db_column="userid")
    name = models.CharField(max_length=64)
    price = models.IntegerField(default=0)
    photo = models.ImageField(upload_to="register/",blank=True)
    date = models.DateField(auto_now=True)
    amount = models.IntegerField(default=0)
    status = models.SmallIntegerField(default=0)

class Order(models.Model):
    user = models.ForeignKey(User,db_column="userid")
    sum = models.IntegerField(default=0)
    mobile = models.CharField(u'手机号',max_length=11, null=True, blank=True)
    email = models.EmailField(u'电子邮箱',max_length=75, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    list= models.TextField(blank=True,null=True)
    desc= models.TextField(blank=True,null=True)
