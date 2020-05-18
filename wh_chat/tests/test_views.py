from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from wh_chat.models import MessagesModel, MapModel


class TestAPIView(TestCase):
    fixtures = ['fixtures.json']
    client = Client()
    url = reverse('wh-chat:api_game', args=[1])  # Valid url

    def test_GET_valid(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_POST_valid(self):
        # test posting messages
        message = {
            'game': '1',
            'author': 'test_author',
            'message': 'test message'
        }
        response = self.client.post(self.url, message)
        self.assertEquals(response.status_code, 201)

        msg_count = MessagesModel.objects.filter(game=1).count()
        self.assertEquals(msg_count, 1)

    def test_POST_invalid(self):
        # test posting messages
        message = {
            'game': '1',
            'author': 'test_author'
        }
        response = self.client.post(self.url, message)
        self.assertEquals(response.status_code, 400)

        msg_count = MessagesModel.objects.filter(game=1).count()
        self.assertEquals(msg_count, 0)

    def test_PUT_valid(self):
        # test updating map
        map_string = MapModel.objects.get(game=1).map
        tactical_map = {
            'game': '1',
            'map': map_string
        }
        client = APIClient()
        response = client.put(self.url, tactical_map)
        self.assertEquals(response.status_code, 202)

    def test_PUT_invalid(self):
        # test updating map
        tactical_map = {
            'game': '1',
            'map': 'gibberish'
        }
        client = APIClient()
        response = client.put(self.url, tactical_map)
        self.assertEquals(response.status_code, 400)

