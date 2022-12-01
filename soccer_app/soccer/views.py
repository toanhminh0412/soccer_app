# from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Game, User

# Dashboard: Allows users to manage their games and teams
class Dashboard(TemplateView):
    template_name = 'soccer/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current user information
        user_id = int(self.request.session.get('user_id', -1))
        
        # Get all games that this user is an organizer
        context['your_games'] = []
        for game in Game.objects.all():
            if len(game.organizers.filter(id=user_id)) > 0:
                context['your_games'].append(game)

        return context

# GamesView that shows all the currently active game
class GamesView(ListView):
    model = Game
    template_name = "soccer/games.html"
    context_object_name = "all_games"

# A game detail page
class GameDetailView(DetailView):
    model = Game
    template_name = "soccer/game_detail.html"
    pk_url_kwarg = "game_id"
    context_object_name = "game"