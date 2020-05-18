from django.test import SimpleTestCase
from django.urls import resolve, reverse
from wh_chat.views import ChatView, GmRoomView


class TestUrls(SimpleTestCase):
    """
    Checks if correct views are called
    """
    def test_HomeView_url(self):
        url = reverse('wh-chat:api_game', args=[1])
        self.assertEquals(resolve(url).func.view_class, ChatView)

    def test_ApiInfoView_url(self):
        url = reverse('wh-chat:gm_room', args=[1])
        self.assertEquals(resolve(url).func.view_class, GmRoomView)
