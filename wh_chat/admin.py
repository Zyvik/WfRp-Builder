from django.contrib import admin
from .models import GameModel, MessagesModel, MapModel


admin.site.register(GameModel)
admin.site.register(MessagesModel)
admin.site.register(MapModel)
