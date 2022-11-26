from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from .forms import GameForm
from .models import User, Game, GameTeam

# Create a new game
def create_game(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        # Get current user, which will be set to be the game organizer
        current_user = User.objects.get(id=request.session['user_id'])
        if form.is_valid():
            game_data = form.cleaned_data
            # Create a new game with the information provided from the create new game form
            new_game = Game.objects.create(
                name = game_data['name'],
                date = game_data['date'],
                location = game_data['location'],
                max_player_num = game_data['max_player_num'],
                team_num = game_data['team_num'],
                visible_to_everyone = game_data['visible_to_everyone'],
                description = game_data['description']
            )
            # Add the current user as the game's organizer
            new_game.organizers.add(current_user)
            new_game.save()

            # Make new teams for the game based on number of teams specified
            for i in range (0, new_game.team_num):
                GameTeam.objects.create(game=new_game, team_number=i)

            # Game creator is originally put on the bench
            new_game_bench = new_game.gameteam_set.get(team_number=0)
            new_game_bench.players.add(current_user)
            new_game_bench.save()

            # Pass a success message into homepage's context
            request.session['success'] = True
            request.session['message'] = 'Game created successfully'
            return redirect('/')
        
        # Pass a failure message into homepage's context
        request.session['success'] = False
        request.session['message'] = 'Failed to create game'
        return redirect('/')

    # Sending other methods to this view will receive an 404
    return HttpResponseNotFound("<h1>404</h1> This page doesn't support this method")

