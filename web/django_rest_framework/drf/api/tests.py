from django.test import TestCase

# Create your tests here.

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase


from .models import Image, Instance, Network

User = get_user_model()

class InstanceCreateTest(APITestCase):
    URL = reverse('instance-list')
    
    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 
                                'admin@mail.com', 'password')
        self.normaluser = User.objects.create_user('test', 
                                'test@mail.com', 'password') 
        self.image = Image.objects.create(name="test", user=self.normaluser)
        self.network = Network.objects.create(name="test", user=self.normaluser)
        self.data = {
                        'name': 'mike', 
                        'count': 1,
                        "networks": [self.network.pk,],
                        "image": self.image.pk,
                    }


    def test_can_create_instance(self):
        response = self.client.post(self.URL, self.data)
        print Instance.objects.first().networks.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 

    def test_can_edit_instance(self):
        response = self.client.post(self.URL, self.data)
        #print Instance.objects.all().first().__dict__
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) 


