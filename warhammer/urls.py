from django.urls import path
from . import views

app_name = 'wh'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('nowy/', views.choose_race, name='race'),
    path('nowy/<slug:race_slug>', views.roll_stats, name='stats'),
    path('profesja/', views.profession_list, name='professions'),
    path('profesja/<slug:profession_slug>', views.profession_detail, name='selected_profession'),
    path('bohater/<slug:pk>', views.CharacterScreen.as_view(), name='character_screen'),
    path('rejestracja', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('kontakt', views.ContactView.as_view(), name='contact'),
    path('api/game/<slug:game_id>', views.ChatView.as_view(), name='api-game'),
    path('game/<slug:game_id>', views.game_master_room, name='gm_room'),
    path('umiejetnosci', views.skills_list, name='skills_list'),
    path('zdolnosci', views.abilities_list, name='abilities_list')
]
