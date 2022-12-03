from django.urls import path
from . import views
from . import invisible_views

urlpatterns = [
    # Visible views
    path('', views.Dashboard.as_view(), name='dashboard'),
    path('game', views.GamesView.as_view(), name='soccer_homepage'),
    path('game/<int:game_id>', views.GameDetailView.as_view(), name='game_detail'),
    
    # Invisible views
    path('create_game', invisible_views.modify_game, name='create_game'),
    path('edit_game/<int:game_id>', invisible_views.modify_game, name='edit_game'),
    path('join_game/<int:game_id>', invisible_views.join_game, name='join_game'),
    path('delete_game/<int:game_id>', invisible_views.delete_game, name='delete_game'),

    path('create_group', invisible_views.modify_group, name='create_group'),
]
