from rest_framework import serializers

from .models import User, Image, Keypair, Network, Instance


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', )


class BaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = None


class CloudBaseSerializer(BaseSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = None


class ImageSerializer(CloudBaseSerializer):

    class Meta:
        model = Image


class KeypairSerializer(CloudBaseSerializer):

    class Meta:
        model = Keypair


class NetworkSerializer(CloudBaseSerializer):

    class Meta:
        model = Network


class InstanceSerializer(CloudBaseSerializer):
    image_info = ImageSerializer(source="image", read_only=True)
    networks = NetworkSerializer(many=True)

    class Meta:
        model = Instance
