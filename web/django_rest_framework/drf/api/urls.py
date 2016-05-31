from django.conf.urls import url, include

from .api import InstanceList

instance_urls = [
    url(r'^$', InstanceList.as_view(), name='instance-list')
]

urlpatterns = [
    url(r'^instances/', include(instance_urls)),
]
