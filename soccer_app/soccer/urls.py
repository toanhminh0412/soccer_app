from django.urls import path
from . import views
from . import invisible_views

urlpatterns = [
    path('', views.Homepage.as_view(), name='soccer_homepage'),
    path('create_game/', invisible_views.create_game, name='create_game'),
    path('game/<int:game_id>/', views.GameDetailView.as_view(), name='game_detail'),
]
