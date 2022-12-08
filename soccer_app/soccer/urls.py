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

    path('create_group', invisible_views.modify_group, name='create_group'),
    path('edit_group/<int:group_id>', invisible_views.modify_group, name='edit_group'),
    path('delete_group/<int:group_id>', invisible_views.delete_group, name='delete_group'),
]
