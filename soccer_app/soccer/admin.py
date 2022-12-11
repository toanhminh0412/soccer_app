from django.contrib import admin
from .models import User, Team, TeamAdmin, Game, GameTeam, Request

# Register your models here.
admin.site.register(User)
admin.site.register(Team)
admin.site.register(TeamAdmin)
admin.site.register(Game)
admin.site.register(GameTeam)
admin.site.register(Request)