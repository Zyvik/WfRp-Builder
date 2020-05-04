from django.urls import path
from . import views

app_name = 'wh'
urlpatterns = [
    path('', views.index, name='index'),
    path('nowy/', views.choose_race, name='race'),
    path('nowy/<slug:race_slug>', views.roll_stats, name='stats'),
    path('profesja/', views.professions, name='professions'),
    path('profesja/<slug:profession_slug>', views.selected_profession, name='selected_profession'),
    path('bohater/<slug:pk>', views.character_screen, name='character_screen'),
    path('rejestracja', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout',views.logout_view, name='logout'),
    path('kontakt',views.contact, name='contact'),
    path('api/game/<slug:game_id>', views.ChatView.as_view(), name='api-game'),
    path('game/<slug:game_id>', views.game_master_room, name='gm_room'),
    path('umiejetnosci', views.skills_list, name='skills_list'),
    path('zdolnosci', views.abilities_list, name='abilities_list')


]