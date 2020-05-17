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

    def validate(self, data):
        """ Validate map string """
        try:
            map_obj = MapModel.objects.get(pk=data['game'].pk)
        except MapModel.DoesNotExist:
            raise serializers.ValidationError("Map doesn't exist.")

        map_list = data['map'].split(',')

        # check if map consist of exclusively integers
        try:
            map_int_list = list(map(int, map_list))
        except ValueError:
            raise serializers.ValidationError("Tokens should be numbers")

        # check map's size
        map_field = map_obj.columns * map_obj.rows
        if len(map_int_list) != map_field + map_obj.tokens + 1:
            raise serializers.ValidationError("Wrong map length")

        # map should start with: 0,1,2,3,..., number of tokens
        if map_int_list[:map_obj.tokens + 1] != list(range(map_obj.tokens + 1)):
            raise serializers.ValidationError("Wrong token declaration")

        return data
