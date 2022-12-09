from django import forms
from .models import Game, Team

# Form for creating a new game
class GameForm(forms.ModelForm):
    team = forms.CharField(max_length=10)

    class Meta:
        model = Game
        fields = ['name', 'date', 'location', 'max_player_num', 'team_num', 'visible_to_everyone', 'description']

# Form for creating a new team
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'max_member_num', 'description']

# Form for updating players for a game's team
class GameTeamForm(forms.Form):
    team_number = forms.IntegerField()
    players = forms.CharField(max_length=300, required=False)
