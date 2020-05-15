from django.urls import path
from . import views

app_name = 'wh-chat'
urlpatterns = [
    path('<int:pk>', views.ChatView.as_view(), name='api-game'),
    path('room/<int:pk>', views.game_master_room, name='gm_room')
]