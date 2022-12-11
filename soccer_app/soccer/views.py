# from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Game, User, TeamAdmin, Team
from .mixins import MessageViewMixin

# Dashboard: Allows users to manage their games and teams
class Dashboard(MessageViewMixin, TemplateView):
    template_name = 'soccer/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current user information
        user_id = int(self.request.session.get('user_id', -1))
        user = User.objects.get(id=user_id)
        
        # Get all games that this user is an organizer
        context['your_games'] = []
        for game in Game.objects.all():
            if len(game.organizers.filter(id=user_id)) > 0:
                context['your_games'].append(game)

        # Get all groups that this user is an admin
        context['your_groups_as_captain'] = []
        context['your_groups_as_cocaptain'] = []
        for team_admin in user.teamadmin_set.all():
            if team_admin.captain:
                context['your_groups_as_captain'].append(team_admin.team)
            else:
                context['your_groups_as_cocaptain'].append(team_admin.team)

        return context

# GamesView that shows all the currently active game
class GamesView(ListView):
    model = Game
    template_name = "soccer/games.html"
    context_object_name = "all_games"

# A game detail page
class GameDetailView(MessageViewMixin, DetailView):
    model = Game
    template_name = "soccer/game_detail.html"
    pk_url_kwarg = "game_id"
    context_object_name = "game_detail"

# GroupsView that shows all the currently active groups
class GroupsView(MessageViewMixin, ListView):
    model = Team
    template_name = "soccer/groups.html"
    context_object_name = "all_groups"

# A group detail page
class GroupDetailView(DetailView):
    model = Team
    template_name = "soccer/group_detail.html"
    pk_url_kwarg = "group_id"
    context_object_name = "group_detail"