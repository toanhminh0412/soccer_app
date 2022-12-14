import re

from django.shortcuts import redirect

# This paths are unaffected by the middleware
LOGIN_PATH = "/login"
ADMIN_PATH = "/admin/"
STATIC_PATH = "static/*"
LOGOUT_PATH = "/logout"
SIGNUP_PATH = "/signup"
RESET_PASSWORD_PATH = "/reset_password"
FAVICON_PATH = "/favicon.ico"

class AuthMiddleware():
    """
    This middleware checks if user is authenticated before every view.
    An unauthenticated user will be redirected to the login page
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # redirect user to login page if user is not authenticated
        if not re.match(request.path, STATIC_PATH)\
        and request.path not in (LOGIN_PATH, LOGOUT_PATH, SIGNUP_PATH, RESET_PASSWORD_PATH, FAVICON_PATH)\
        and ADMIN_PATH not in request.path\
        and not request.session.get('user_id', None):
            # If an authenticated user clicks on a link to join game,
            # they will be redirected to the join game url after logging in
            if ('join_game' in request.path or 'join_group' in request.path) and not request.session.get('user_id', None):
                request.session['redirect_url'] = request.path
                request.session['redirect_message'] = "Please login before you can join. If you don't have an account, please signup."

            return redirect('/login')

        response = self.get_response(request)

        return response
