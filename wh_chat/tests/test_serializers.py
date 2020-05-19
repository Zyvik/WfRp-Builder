from django.test import TestCase
from wh_chat.models import MessagesModel, MapModel
from wh_chat.serializers import MapSerializer, ChatSerializer


class TestSerializers(TestCase):
    fixtures = ['fixtures.json']

    def test_ChatSerializer(self):
        # valid
        message = {'game': 1, 'author': 'foo', 'message': 'bar'}
        serializer = ChatSerializer(data=message)
        self.assertTrue(serializer.is_valid())

        # No game
        message = {'author': 'foo', 'message': 'bar'}
        serializer = ChatSerializer(data=message)
        self.assertFalse(serializer.is_valid())

        # No author
        message = {'game': 1, 'message': 'bar'}
        serializer = ChatSerializer(data=message)
        self.assertFalse(serializer.is_valid())

        # Multiple valid messages at once
        messages = [
            {'game': 1, 'author': 'foo', 'messages': 'bar'},
            {'game': 1, 'author': 'foo', 'messages': 'bar'},
            {'game': 1, 'author': 'foo', 'messages': 'bar'}
        ]
        serializer = ChatSerializer(data=messages)
        self.assertFalse(serializer.is_valid())

    def test_MapSerializer(self):
        map_obj = MapModel.objects.get(id=1)
        map_str = map_obj.map

        # Valid
        map_msg = {'game': 1, 'map': map_str}
        serializer = MapSerializer(map_obj, data=map_msg)
        self.assertTrue(serializer.is_valid())

        # wrong token declaration
        map_str = map_obj.map.replace('0', '8', 1)
        map_msg = {'game': 1, 'map': map_str}
        serializer = MapSerializer(map_obj, data=map_msg)
        self.assertFalse(serializer.is_valid())

        # wrong map length
        map_str = map_obj.map + ',0'
        map_msg = {'game': 1, 'map': map_str}
        serializer = MapSerializer(map_obj, data=map_msg)
        self.assertFalse(serializer.is_valid())

        # Non integer as a token
        map_list = map_obj.map.split(',')
        # change 1st field after token declaration
        map_list[map_obj.tokens + 1] = 'foobar'
        map_str = ','.join(map_list)
        map_msg = {'game': 1, 'map': map_str}
        serializer = MapSerializer(map_obj, data=map_msg)
        self.assertFalse(serializer.is_valid())
