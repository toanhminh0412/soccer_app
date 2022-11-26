from django import forms
from .models import Game

# Form for creating a new game
class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'team', 'date', 'location', 'max_player_num', 'team_num', 'visible_to_everyone', 'description']