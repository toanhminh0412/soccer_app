from functools import wraps
from .models import User, Game 

from django.http import JsonResponse

def is_organizer(function_view):
    @wraps(function_view)
    def decorate(*args, **kwargs):
        request = kwargs['request']
        game_id = kwargs['game_id']
        user = User.objects.get(id=int(request.session['user_id']))
        game = Game.objects.get(id=game_id)
        if not game.is_organizer(user):
            return JsonResponse({'status': 403, 'message': 'User is not authorized to access this page'})
        return function_view(**args, **kwargs)
    return decorate