from rest_framework import generics, permissions

from rest_framework.response import Response
from .serializers import (UserSerializer, ImageSerializer, KeypairSerializer,
                          NetworkSerializer, InstanceSerializer)
from .models import User, Instance



class InstanceList(generics.ListCreateAPIView):
    #model = Instance
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = InstanceSerializer(data=request.data,
                                      context={"request": request})
        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            name = "%s-%04d" % (name, 1)
            ins = serializer.save(name=name)
        
        return Response(serializer.data)
