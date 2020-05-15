from django.contrib import admin
from .models import GameModel, MessagesModel, MapModel
# Register your models here.
admin.site.register(GameModel)
admin.site.register(MessagesModel)
admin.site.register(MapModel)
