from django.contrib import admin
from .models import SoccerUser, Group, GroupAdmin, Game, GameTeam, Request

# Register your models here.
admin.site.register(SoccerUser)
admin.site.register(Group)
admin.site.register(GroupAdmin)
admin.site.register(Game)
admin.site.register(GameTeam)
admin.site.register(Request)