from django.urls import path
from . import views

app_name = 'wh'
urlpatterns = [
    path('', views.index, name = 'index'),
    path('nowy/', views.choose_race, name='race'),
    path('nowy/<slug:race_slug>', views.RollStats.as_view(), name='stats'),
    path('nowy/<slug:race_slug>/<slug:pk>', views.CustomizeCharacter, name='custom'),
    path('profesja/', views.professions, name='professions'),
    path('profesja/<slug:profession_slug>', views.selected_profession, name='selected_profession'),
    path('test/', views.test, name='test'),
    path('bohater/<slug:pk>', views.character_screen, name='character_screen'),
    path('rejestracja', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout',views.logout_view, name='logout'),
    path('kontakt',views.contact, name='contact'),
    path('api/chat/<slug:game_id>', views.ChatView.as_view(), name='api-chat'),
    path('chat', views.chat)

]