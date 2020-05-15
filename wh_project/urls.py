from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('warhammer/', include('warhammer.urls', namespace='wh')),
    path('warhammer/chat/', include('wh_chat.urls', namespace='wh_chat'))
]
