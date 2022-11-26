# from django.shortcuts import render
# from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Game

# Create your views here.
# Homepage that shows all the currently active game
class Homepage(ListView):
    model = Game
    template_name = "soccer/home.html"
    context_object_name = "all_games"

# A game detail page
class GameDetailView(DetailView):
    model = Game
    template_name = "soccer/game_detail.html"
    pk_url_kwarg = "game_id"
    context_object_name = "game"