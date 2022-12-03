from django import forms
from .models import Game, Team

# Form for creating a new game
class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name', 'team', 'date', 'location', 'max_player_num', 'team_num', 'visible_to_everyone', 'description']

# Form for creating a new team
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'max_member_num', 'description']