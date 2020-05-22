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
        map_obj = self._get_map(data['game'].pk)
        map_list = data['map'].split(',')
        map_int_list = self._convert_str_list_to_int_list(map_list)

        self._check_map_size(map_obj, map_int_list)
        self._check_token_declaration(map_obj, map_int_list)

        return data

    def _get_map(self, pk):
        try:
            map_object = MapModel.objects.get(pk)
        except MapModel.DoesNotExist:
            raise serializers.ValidationError("Map doesn't exist.")
        return map_object

    def _convert_str_list_to_int_list(self, map_list):
        try:
            map_int_list = list(map(int, map_list))
        except ValueError:
            raise serializers.ValidationError("Tokens should be numbers")
        return map_int_list

    def _check_map_size(self, map_obj, map_int_list):
        map_field = map_obj.columns * map_obj.rows
        if len(map_int_list) != map_field + map_obj.tokens + 1:
            raise serializers.ValidationError("Wrong map length")

    def _check_token_declaration(self, map_obj, map_int_list):
        # map should start with: 0,1,2,3,..., number of tokens
        if map_int_list[:map_obj.tokens + 1] != list(range(map_obj.tokens + 1)):
            raise serializers.ValidationError("Wrong token declaration")
