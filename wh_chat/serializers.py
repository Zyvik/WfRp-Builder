from rest_framework import serializers
from .models import MessagesModel, MapModel


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesModel
        fields = ('pk', 'game', 'author', 'message')


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapModel
        fields = ('game', 'map')
