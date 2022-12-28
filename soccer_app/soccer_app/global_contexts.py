# pylint:
from soccer.models import SoccerUser

# Get current user information
def get_user(request):
    user_id = request.session.get('user_id', None)

    # if user is not logged in, return None for all values
    if not user_id:
        return {
            'soccer_user': None,
            'user_id': None,
            'name': None,
            'phone_number': None
        }
    
    name = request.session.get('name')
    phone_number = request.session.get('phone_number')
    return {
        'soccer_user': SoccerUser.objects.get(id=user_id),
        'user_id': user_id,
        'name': name,
        'phone_number': phone_number
    }
