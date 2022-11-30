# pylint:
from soccer.models import User

# Get current user information
def get_user(request):
    user_id = request.session.get('user_id', None)
    name = request.session.get('name')
    phone_number = request.session.get('phone_number')
    return {
        'user_id': user_id,
        'name': name,
        'phone_number': phone_number
    }
