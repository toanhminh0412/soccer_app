from django.urls import path
from . import views
from . import invisible_views

urlpatterns = [
    # Visible views
    path('', views.Dashboard.as_view(), name='dashboard'),

    path('game', views.GamesView.as_view(), name='games'),
    path('game/<int:game_id>', views.GameDetailView.as_view(), name='game_detail'),

    path('group', views.GroupsView.as_view(), name='groups'),
    path('group/<int:group_id>', views.GroupDetailView.as_view(), name='group_detail'),
    
    # Invisible views
    path('create_game', invisible_views.modify_game, name='create_game'),
    path('edit_game/<int:game_id>', invisible_views.modify_game, name='edit_game'),
    path('join_game/<int:game_id>', invisible_views.join_game, name='join_game'),
    path('delete_game/<int:game_id>', invisible_views.delete_game, name='delete_game'),
    path('update_players/<int:game_id>', invisible_views.update_players, name='update_players'),
    path('remove_player_from_game/<int:game_id>/<int:player_id>', invisible_views.remove_player_from_game,
    name='remove_player_from_game'),
    path('player_leave_game/<int:game_id>', invisible_views.player_leave_game, name='player_leave_game'),
    path('leave_group/<int:group_id>', invisible_views.leave_group, name='leave_group'),

    path('create_group', invisible_views.modify_group, name='create_group'),
    path('edit_group/<int:group_id>', invisible_views.modify_group, name='edit_group'),
    path('join_group/<int:group_id>', invisible_views.join_group, name='join_group'),
    path('request_to_join_group/<int:group_id>', invisible_views.request_to_join_group, name='request_to_join_group'),
    path('delete_group/<int:group_id>', invisible_views.delete_group, name='delete_group'),
    path('remove_member_from_group/<int:group_id>/<int:member_id>', invisible_views.remove_member_from_group,
    name='remove_member_from_group'),

    path('accept_request/<int:request_id>', invisible_views.accept_request, name='accept_request'),
    path('decline_request/<int:request_id>', invisible_views.decline_request, name='decline_request')
]
