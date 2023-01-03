import os
from twilio.rest import Client

from django.http import JsonResponse
from django.shortcuts import redirect
from .forms import GameForm, GroupForm, GameTeamForm
from .models import SoccerUser, Game, GameTeam, Group, GroupAdmin, Request

# Enable the line below if need to specify the path of .env file
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Get access information for Twilio
account_sid = os.environ.get('TWILIO_ACCOUNT_SID', None)
auth_token = os.environ.get('TWILIO_AUTH_TOKEN', None)
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER', None)

###################################
######### Helper functions ########
###################################
# Get current user
def get_user(request):
    return SoccerUser.objects.get(id=int(request.session['user_id']))

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

            if game_data['group'] != 'none':
                new_game.group = Group.objects.get(id=int(game_data['group']))

            else:
                new_game.group = None
            new_game.save()

            if new_game.group and not game_id:
                group = new_game.group
                # Send an SMS message to every member in the group information about the game
                # with an invitation link
                client = Client(account_sid, auth_token)
                for member in group.members.all():
                    print('sending a message')
                    message = client.messages\
                    .create(
                        body=(f"Group {group.name} has a new game:\n"
                            f"Name: {new_game.name}\n"
                            f"Date: {new_game.date}\n"
                            f"Location: {new_game.location}\n"
                            f"Max players: {new_game.max_player_num}\n"
                            f"Number of teams: {new_game.team_num}\n"
                            f"Description: {new_game.description}\n"
                            "If you would like to join the game, click the link down below:\n"
                            f"https://{request.get_host()}/join_game/{new_game.id}\n"
                            "Have a good day!!"),
                        from_=twilio_phone_number,
                        to=f'+1{member.phone_number}'
                    )
                    print(message.sid)

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
        # return JsonResponse({'status': 400, 'message': "You are already in this game"})
        return redirect(f'/game/{game_id}')

    game.gameteam_set.get(team_number=0).players.add(user)
    
    request.session['success'] = True
    request.session['message'] = f'Joined game {game.name} successfully'

    return redirect(f'/game/{game_id}')

# Exit game
def player_exit(request, game_id):
    if request.method == "GET":
        # Get current user
        current_user = get_user(request)
        user_id = int(request.session['user_id'])
        try:
            game = Game.objects.get(id=game_id)
            team_num = GameTeam.objects.get(players=user_id,game=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'status': 404, 'message': 'Game not found'})
        game.gameteam_set.get(team_number=team_num.team_number).players.remove(current_user)

    request.session['success'] = True
    request.session['message'] = f'Exit game {game.name} successfully'

    return redirect(f'/game')

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

# Admin View: Modify players for a team of a game
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
            return JsonResponse({'status': 403, 'message': 'You are not authorized to edit players for this team'})
        
        form = GameTeamForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            team_number = data['team_number']
            if 'players' in data:
                player_ids = data['players'].split(',')
            else:
                player_ids = ''

            team = game.gameteam_set.filter(team_number=team_number)
            if len(team) == 0:
                return JsonResponse({'status': 404, 'message': 'Group not found'})
            
            team = team[0]
            bench = game.get_bench()
            # Remove the team assigned players from bench
            for player in bench.players.all():
                if str(player.id) in player_ids:
                    bench.players.remove(player)

            # Add players to the team
            current_team_players = list(team.players.all())
            team.players.clear()
            for id in player_ids:
                if id != '':
                    player = SoccerUser.objects.get(id=int(id))
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
        
        form = GroupForm(request.POST)

        if form.is_valid():
            group_data = form.cleaned_data
            
            new_group = None
            # Edit an existing group
            if group_id:
                new_group = Group.objects.get(id=group_id)
            # Create a new group
            else:
                new_group = Group()

            new_group.name = group_data['name']
            if group_data['max_member_num'] is not None or group_data['max_member_num'] != -1:
                new_group.max_member_num = group_data['max_member_num']
            new_group.description = group_data['description']
            new_group.save()

            if not group_id:
                new_group.members.add(current_user)

                # Make the creator captain of group
                GroupAdmin.objects.create(group=new_group, user=current_user, captain=True)

            # Pass a success message into homepage's context
            request.session['success'] = True
            request.session['message'] = f'Group {new_group.name} edited successfully' if group_id else f'Group {new_group.name} created successfully'
            return redirect('/#groups')

    # Sending other methods to this view will receive an 400
    return JsonResponse({'status': 400, 'message': "This page doesn't support this method"})

# Send a request to the group admins to join the group
def request_to_join_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Group not found'})

    # Get current user
    current_user = get_user(request)

    # Return 400 if the user is already in the group
    if current_user in group.members.all():
        return JsonResponse({'status': 400, 'message': 'You are already in this group'})

    # Return 400 if the user has already requested to join the group
    if len(Request.objects.filter(user=current_user, group=group)) > 0:
        return JsonResponse({'status': 400, 'message': 'You already requested to join this group'})

    # Create a request, flash a success message and redirect to groups page
    Request.objects.create(type='group', user=current_user, group=group)
    request.session['success'] = True
    request.session['message'] = f'Requested to join group {group.name}'

    return redirect('/group')

# Join group using an invite link
def join_group(request, group_id):
    # Return 404 if group is not found
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Group not found'})

    # Get current user
    current_user = get_user(request)

    # Return 400 if the user is already in the group
    if current_user in group.members.all():
        return redirect(f'/group/{group_id}')
    
    # Delete the request to join group that this user already sent if any
    join_request = Request.objects.filter(user=current_user, group=group)
    if len(join_request) > 0:
        for jr in join_request:
            jr.delete()

    group.members.add(current_user)
    request.session['success'] = True
    request.session['message'] = f'Joined group {group.name} successfully'

    return redirect(f'/group/{group_id}')

# Delete a group
def delete_group(request, group_id):
    # Return 404 if group is not found
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Group not found'})
    
    # Get current user
    current_user = get_user(request)
    
    # Non-captain (co-captains included) users can't delete group
    if len(GroupAdmin.objects.filter(group=group, user=current_user, captain=True)) == 0:
        return redirect('/#groups')

     # Delete the group. Display success message
    name = group.name
    group.delete()
    request.session['success'] = True
    request.session['message'] = f'Group {name} deleted successfully'

    return redirect('/#groups')

# Accept a request to join a game or group
def accept_request(request, request_id):
    # Return 404 if request not found
    try:
        join_request = Request.objects.get(id=request_id)
    except Group.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Request not found'})

    current_user = get_user(request)

    # Request to join a group
    if join_request.group:
        # Non-admin group member can't accept a request
        if len(join_request.group.groupadmin_set.filter(user=current_user)) == 0:
            return JsonResponse({'status': 403, 'message': 'You are unauthorized to visit this url'})

        # Add member to the group and delete the request
        join_request.group.members.add(join_request.user)
        join_request.delete()

    # Request to join a game
    if join_request.game:
        # Non-organizer game player can't accept a request
        if not join_request.game.is_organizer(current_user):
            return JsonResponse({'status': 403, 'message': 'You are unauthorized to visit this url'})

        # Add player to the game and delete the request
        join_request.game.get_bench().players.add(join_request.user)
        join_request.delete()

    # Display success message and redirect to dashboard for requests
    request.session['success'] = True
    request.session['message'] = f'Request accepted successfully'

    return redirect('/#requests')

# Decline a request to join a game or group
def decline_request(request, request_id):
    # Return 404 if request not found
    try:
        join_request = Request.objects.get(id=request_id)
    except Group.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Request not found'})

    current_user = get_user(request)

    # Request to join a group
    if join_request.group:
        # Non-admin group member can't decline a request
        if len(join_request.group.groupadmin_set.filter(user=current_user)) == 0:
            return JsonResponse({'status': 403, 'message': 'You are unauthorized to visit this url'})

    # Request to join a game
    if join_request.game:
        # Non-organizer game player can't decline a request
        if not join_request.game.is_organizer(current_user):
            return JsonResponse({'status': 403, 'message': 'You are unauthorized to visit this url'})

    # delete the request
    join_request.delete()

    # Display success message and redirect to dashboard for requests
    request.session['success'] = True
    request.session['message'] = f'Request declined successfully'

    return redirect('/#requests')