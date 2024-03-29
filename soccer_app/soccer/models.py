from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

from pytz import timezone
from django_random_id_model import RandomIDModel

# Create your models here.
# SoccerUser model of this application
class SoccerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    phone_number = models.CharField(max_length=10, null=False, blank=False, validators=[RegexValidator(regex='[0-9]{10}')])
    last_active = models.DateTimeField(auto_now=True)

    # Name of the table is 'soccer_user'
    # The entries are sorted by id
    class Meta:
        db_table = 'soccer_custom_user'

    # Get full name of the user
    def get_full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    def __str__(self):
        return self.get_full_name()

    # Get all teams that are managed by this user
    def get_managed_groups(self):
        groups = []
        for groupadmin in self.groupadmin_set.all():
            groups.append(groupadmin.group)
        return groups

# Groups:
# - There is a captain and co-captains in a team. These people can create/modify games for this team. They can also build teams.
# - Group members can join games without having to request the captain or co-captains. They can choose to join a team, which can be changed later
# by the captain or co-captains, or choose to be on the bench waiting to be arranged.
# - Games of a team can be set to be visible to outsiders.
# - Outsiders must request team captain or co-captains to join the team's games.
# - Everytime a game is created or modified, team members are notified
class Group(RandomIDModel):
    name = models.CharField(max_length=50, null=False, blank=False)
    max_member_num = models.IntegerField(null=True, blank=True)
    members = models.ManyToManyField(SoccerUser)
    description = models.CharField(max_length=300, null=False, blank=False)

    class Meta:
        db_table = 'soccer_team'
        ordering = ['name']

    def __str__(self):
        return self.name

    # Return type: a GroupAdmin
    # Return value: the captain of a group
    def get_captain(self):
        return self.groupadmin_set.get(captain=True)

    # Return type: list of SoccerUser
    # Return value: a list of all group admins
    def get_admins(self):
        admins = []
        for admin in self.groupadmin_set.all():
            admins.append(admin.user)
        return admins

    # Returns a string that contains all co-captains' names separated by a comma
    def get_cocaptains_str(self):
        cocaptains = self.groupadmin_set.filter(captain=False)
        cocaptains_str = ''
        for cocaptain in cocaptains:
            cocaptains_str += f'{cocaptain}, '
        return cocaptains_str[:-2] if cocaptains_str != '' else 'None'

    # Get all users that have requested to join this group
    def get_requested_users(self):
        users = []
        for request in self.request_set.all():
            users.append(request.user)
        return users

# Group admins are captains or co-captains of groups
class GroupAdmin(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(SoccerUser, on_delete=models.CASCADE, null=False, blank=False)
    # True if user is the captain, otherwise false, which means user is a co-captain
    captain = models.BooleanField(null=False, blank=False)

    class Meta:
        db_table = 'soccer_group_admin'
        ordering = ['user']

    def __str__(self):
        return f'{self.user} in {self.group.name}'

# Games:
# - Anyone can create/modify a game. This owner of a game is called the organizer. Organizer can build teams
# - Everyone can see and join game without sending request to the organizer
# - They can join a game team or join bench waiting to be arranged.
class Game(RandomIDModel):
    name = models.CharField(max_length=50, null=False, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    organizers = models.ManyToManyField(SoccerUser)
    date = models.DateTimeField(null=False, blank=False)
    location = models.CharField(max_length=200, null=False, blank=False, default='location')
    max_player_num = models.IntegerField(null=True, blank=True)
    team_num = models.IntegerField(default=2, validators=[MinValueValidator(1), MaxValueValidator(8)])
    visible_to_everyone = models.BooleanField(default=True)
    description = models.CharField(max_length=300, null=False, blank=False)

    class Meta:
        db_table = 'soccer_team_game'
        ordering = ['date']

    def __str__(self):
        return self.name

    # Calculate total players participating in a game
    def total_players(self):
        players = 0
        for team in self.gameteam_set.all():
            players = players + team.players.count()
        return players

    # Get the creator of a game, who is the first member of organizers
    def get_creator(self):
        return self.organizers.first()

    # Get bench - team number 0 of a game
    def get_bench(self):
        return self.gameteam_set.get(team_number=0)

    # Get all teams of a game other than the bench
    def get_teams(self):
        return self.gameteam_set.exclude(team_number=0)

    # Get number of teams rendered on a row based on the game's number of teams on a large (lg) screen
    def get_team_num_on_a_row_lg(self):
        if self.team_num == 1:
            return 1
        if self.team_num == 2:
            return 2
        if self.team_num < 7:
            return 3
        return 4

    # Return a list of all players
    def get_players(self):
        players = []
        for team in self.gameteam_set.all():
            players.extend(team.players.all())
        return players

    # Get string representation of a game's date
    def get_date_str(self):
        return self.date.astimezone(timezone('PST8PDT')).strftime('%Y-%m-%dT%H:%M')

    # Check if an user is an organizer of a game
    def is_organizer(self, user):
        return len(self.organizers.filter(id=user.id)) > 0

# Groups for a specific game. A game can have one or many teams that include players 
# who participate in that game
class GameTeam(models.Model):
    players = models.ManyToManyField(SoccerUser)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False)
    # If set to 0, the team is a bench, which mean players are not assigned to any team
    team_number = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = 'soccer_game_team'
        ordering = ['game']

    def __str__(self):
        return f'Group {self.team_number} of game {self.game.name}'

    # Assign a color to a game team based on the team's number
    def get_color(self):
        match self.team_number:
            case 1:
                return "bg-blue-200"
            case 2:
                return "bg-red-200"
            case 3:
                return "bg-green-200"
            case 4:
                return "bg-yellow-200"
            case 5:
                return "bg-purple-200"
            case 6:
                return "bg-pink-200"
            case 7:
                return "bg-orange-200"
            case 8:
                return "bg-teal-200"
            case _:
                return "bg-light"

    # Return all players name in a string, separated by a comma
    def get_player_names(self):
        names = ''
        for player in self.players.all():
            names += str(player) + ','
        return names

    # Return all players id in a string, separated by a comma
    def get_player_ids(self):
        ids = ''
        for player in self.players.all():
            ids += str(player.id) + ','
        return ids

# A request to join a game or a group
# Request has to be accepted by an admin for a player to join a game or a group
class Request(models.Model):
    type = models.CharField(max_length=5, choices=[('group', 'group'), ('game', 'game')], default='group')
    # Sender of the request
    user = models.ForeignKey(SoccerUser, on_delete=models.CASCADE, null=False, blank=False)
    # Receiver end of the request, depending on the type
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)