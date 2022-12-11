from django.http import JsonResponse
from django.shortcuts import redirect
from .forms import GameForm, TeamForm, GameTeamForm
from .models import User, Game, GameTeam, Team, TeamAdmin, Request

###################################
######### Helper functions ########
###################################
# Get current user
def get_user(request):
    return User.objects.get(id=int(request.session['user_id']))

# Admin View: With no argument - Create a new game
# Admin View: With argument <game_id> - Edit game with id <game_id>
def modify_game(request, **kwargs):
    if request.method == "POST":
        game_id = kwargs.get('game_id', None)

        # Get current user, which will be set to be the game organizer
        current_user = get_user(request)
        if game_id:
            game = Game.objects.get(id=game_id)
            # If user isn't an organizer of the game, redirect to dashboard
            if not game.is_organizer(current_user):
                return redirect('/')

        form = GameForm(request.POST)
        
        if form.is_valid():
            game_data = form.cleaned_data
            print('Group: ' + game_data['team'])
            
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

            if game_data['team'] != 'none':
                new_game.team = Team.objects.get(id=int(game_data['team']))
            new_game.save()

            # Add the current user as the game's organizer
            if not game_id:
                new_game.organizers.add(current_user)
            
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
        if game_id:
            game = Game.objects.get(id=game_id)
        request.session['success'] = False
        request.session['message'] = f'Failed to edit game {game.name}' if game_id else 'Failed to create game'
        return redirect('/')

    # Sending other methods to this view will receive an 400
    return JsonResponse({'status': 400, 'message': "This page doesn't support this method"})


# Normal View: Player joins a game.
def join_game(request, game_id):
    user = get_user(request)

    # Player is put on bench when first join a game
    game = None
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Game not found'})

    # Player can't join a full game
    if game.total_players() >= game.max_player_num:
        return JsonResponse({'status': 400, 'message': "Can't join game. Game is full"})

    # Return 400 if the player is already in the game
    if user in game.get_players():
        return JsonResponse({'status': 400, 'message': "You are already in this game"})

    game.gameteam_set.get(team_number=0).players.add(user)
    
    request.session['success'] = True
    request.session['message'] = f'Joined game {game.name} successfully'

    return redirect(f'/game/{game_id}')

# Admin View: Delete a game
def delete_game(request, game_id):
    # Get current user
    current_user = get_user(request)
    game = None
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        # Display 404 if game not found
        return JsonResponse({'status': 404, 'message': 'Game not found'})
    
    # If user isn't an organizer of the game, redirect to dashboard
    if not game.is_organizer(current_user):
        return redirect('/')
    
    # Delete the game. Display success message
    name = game.name
    game.delete()
    request.session['success'] = True
    request.session['message'] = f'Game {name} deleted successfully'

    return redirect('/')

# Admin View:
def update_players(request, game_id):
    if request.method == "POST":
        # Get current user
        current_user = get_user(request)
        game = None
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            # Display 404 if game not found
            return JsonResponse({'status': 404, 'message': 'Game not found'})

        # If user isn't an organizer of the game, redirect to dashboard
        if not game.is_organizer(current_user):
            return redirect('/')
        
        form = GameTeamForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            team_number = data['team_number']
            if 'players' in data:
                player_names = data['players'].split(',')
            else:
                player_names = ''

            team = game.gameteam_set.filter(team_number=team_number)
            if len(team) == 0:
                return JsonResponse({'status': 404, 'message': 'Team not found'})
            
            team = team[0]
            bench = game.get_bench()
            # Remove the players from bench
            for player in bench.players.all():
                if player.name in player_names:
                    bench.players.remove(player)

            # Add players to the team
            current_team_players = list(team.players.all())
            team.players.clear()
            for name in player_names:
                if name != '':
                    player = User.objects.get(name=name)
                    team.players.add(player)

            team_players = team.players.all()
            # Add removed players from team to bench
            for player in current_team_players:
                if player not in team_players:
                    bench.players.add(player)

            request.session['success'] = True
            request.session['message'] = f'Update players for team {team_number} successfully'
            return redirect(f'/game/{game_id}')
        else:
            request.session['success'] = False
            request.session['message'] = 'Failed to update players for team'
            return redirect(f'/game/{game_id}')

    return JsonResponse({'status': 400, 'message': 'This method is not supported'})


# Create a group
def modify_group(request, **kwargs):
    if request.method == "POST":
        group_id = kwargs.get('group_id', None)

        # Get current user, which will be set to be the group captain
        current_user = get_user(request)
        
        form = TeamForm(request.POST)

        if form.is_valid():
            group_data = form.cleaned_data
            
            new_group = None
            # Edit an existing group
            if group_id:
                new_group = Team.objects.get(id=group_id)
            # Create a new group
            else:
                new_group = Team()

            new_group.name = group_data['name']
            if group_data['max_member_num'] is not None or group_data['max_member_num'] != -1:
                new_group.max_member_num = group_data['max_member_num']
            new_group.description = group_data['description']
            new_group.save()

            if not group_id:
                new_group.members.add(current_user)

                # Make the creator captain of group
                TeamAdmin.objects.create(team=new_group, user=current_user, captain=True)

            # Pass a success message into homepage's context
            request.session['success'] = True
            request.session['message'] = f'Group {new_group.name} edited successfully' if group_id else f'Group {new_group.name} created successfully'
            return redirect('/#groups')

    # Sending other methods to this view will receive an 400
    return JsonResponse({'status': 400, 'message': "This page doesn't support this method"})

# Send a request to the group admins to join the group
def request_to_join_group(request, group_id):
    try:
        group = Team.objects.get(id=group_id)
    except Team.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Group not found'})

    # Get current user
    current_user = get_user(request)

    # Return 400 if the user is already in the group
    if current_user in group.members.all():
        return JsonResponse({'status': 400, 'message': 'You are already in this group'})

    # Reutnr 400 if the user has already requested to join the group
    if len(Request.objects.filter(user=current_user, group=group)) > 0:
        return JsonResponse({'status': 400, 'message': 'You already requested to join this group'})

    # Create a request, flash a success message and redirect to groups page
    Request.objects.create(type='group', user=current_user, group=group)
    request.session['success'] = True
    request.session['message'] = f'Requested to join group {group.name}'

    return redirect('/group')

# Delete a group
def delete_group(request, group_id):
    try:
        group = Team.objects.get(id=group_id)
    except Team.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Group not found'})
    
    # Get current user
    current_user = get_user(request)
    
    # Non-captain (co-captains included) users can't delete group
    if len(TeamAdmin.objects.filter(team=group, user=current_user, captain=True)) == 0:
        return redirect('/#groups')

     # Delete the group. Display success message
    name = group.name
    group.delete()
    request.session['success'] = True
    request.session['message'] = f'Group {name} deleted successfully'

    return redirect('/#groups')