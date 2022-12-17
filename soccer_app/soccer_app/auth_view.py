from django.views.generic import TemplateView
from django import forms
from django.shortcuts import redirect
from django.utils import timezone

from soccer.models import User, Game

# This mixin redirects a view to homepage if the user is logged in
class LoginRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        # redirect to user page if user is already authenticated and is a normal user
        if request.session.get("user_id", None):
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)


# Form for login information validation
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['phone_number', 'name']

# User must login to the application to use app's features
class LoginView(LoginRedirectMixin, TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Display message if any
        context['success'] = self.request.session.get('success', None)
        context['message'] = self.request.session.get('message', None)
        
        # Clear message in session if exists
        if 'success' in self.request.session:
            del self.request.session['success']
        if 'message' in self.request.session:
            del self.request.session['message']
        
        return context

    def post(self, request, **kwargs):
        # Check if the user information is correct
        form = LoginForm(request.POST)
        if form.is_valid():
            user_info = form.cleaned_data
            phone_number = user_info['phone_number']
            name = user_info["name"]
            
            # Check if the user already has an account
            user_exist = User.objects.filter(phone_number=phone_number, name=name)
            
            # If user doesn't have an account, create a new one
            user = None
            if len(user_exist) == 0:
                user = User.objects.create(phone_number=phone_number, name=name)
            else:
                user = user_exist[0]
            
            # Log the user in by saving user info in the app's session
            request.session['user_id'] = user.id
            request.session['phone_number'] = phone_number
            request.session['name'] = name

            # Remove all games in the past
            for game in Game.objects.all():
                if game.date < timezone.now():
                    print(game.date)
                    print(timezone.now())
                    game.delete()
                # This is doable as games are sorted by date
                else:
                    break

            # If an authenticated user clicks on a link to join game,
            # they will be redirected to the join game url after logging in
            redirect_url = request.session.get('redirect_url', None)
            if redirect_url:
                return redirect(redirect_url)

            # Redirect to homepage
            return redirect('/')
        
        # Redirect to login page with an error message (likely never happens)
        else:
            request.session['success'] = False
            request.session['message'] = 'Failed to login. Please try again'
            return redirect('/login/')


# User logout, their user session is deleted but their user information
# is still stored in the database. After logging out user is navigated to the login page
def logout_view(request):
    # Delete user information in the current session
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['phone_number']
        del request.session['name']
    return redirect('/login/')
