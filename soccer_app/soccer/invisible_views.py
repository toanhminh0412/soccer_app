from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from .forms import GameForm
from .models import User, Game, GameTeam

# With no argument: Create a new game
# With argument <game_id>: Edit game with id <game_id>
def modify_game(request, **kwargs):
    if request.method == "POST":
        game_id = kwargs['game_id']

        form = GameForm(request.POST)
        # Get current user, which will be set to be the game organizer
        current_user = User.objects.get(id=request.session['user_id'])
        if form.is_valid():
            game_data = form.cleaned_data
            
            new_game = None
            old_team_num = 0
            if game_id:
                new_game = Game.objects.get(id=game_id)
                old_team_num = new_game.team_num
            else:
                new_game = Game()
            # Update new game with the information provided from the game form
            new_game.name = game_data['name']
            new_game.date = game_data['date']
            new_game.location = game_data['location']
            new_game.max_player_num = game_data['max_player_num']
            new_game.team_num = game_data['team_num']
            new_game.visible_to_everyone = game_data['visible_to_everyone']
            new_game.description = game_data['description']

            # Add the current user as the game's organizer
            if not game_id:
                new_game.organizers.add(current_user)
            
            new_game.save()
            
            if game_id:
                # For editing games, if number of teams is higher then just add teams
                # If number of teams stays the same then don't do anything
                # If number of teams is lower then delete teams from highest number to lowest
                # Players in the deleted teams are put on bench
                if new_game.team_num > old_team_num:
                    for i in range (old_team_num + 1, new_game.team_num + 1):
                        GameTeam.objects.create(game=new_game, team_number=i)
                elif new_game.team_num < old_team_num:
                    new_game_bench = new_game.gameteam_set.get(team_number=0)
                    for i in range (old_team_num, new_game.team_num, -1):
                        team = new_game.gameteam_set.get(team_number=i)
                        for player in team.players.all():
                            new_game_bench.players.add(player)
                        team.delete()
            else:
                # Make new teams for the game based on number of teams specified
                for i in range (0, new_game.team_num + 1):
                    GameTeam.objects.create(game=new_game, team_number=i)

            # Game creator is originally put on the bench
            if not game_id:
                new_game_bench = new_game.gameteam_set.get(team_number=0)
                new_game_bench.players.add(current_user)
                new_game_bench.save()

            # Pass a success message into homepage's context
            request.session['success'] = True
            request.session['message'] = f'Game {new_game.name} edited successfully' if game_id else f'Game {new_game.name} created successfully'
            return redirect('/')
        
        # Pass a failure message into homepage's context
        game = Game.objects.get(id=game_id)
        request.session['success'] = False
        request.session['message'] = f'Failed to edit game {game.name}' if game_id else 'Failed to create game'
        return redirect('/')

    # Sending other methods to this view will receive an 404
    return HttpResponseNotFound("<h1>404</h1> This page doesn't support this method")


# Player joins a game.
def join_game(request, game_id):
    user_id = request.session.get('user_id', None)
    user = User.objects.get(id=user_id)

    # Player is put on bench when first join a game
    game = Game.objects.get(id=game_id)
    game.gameteam_set.get(team_number=0).players.add(user)
    
    return redirect(f'/game/{game_id}/')