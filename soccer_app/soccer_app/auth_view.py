from django.views.generic import TemplateView
from django import forms
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.models import User

from soccer.models import SoccerUser, Game

# This mixin redirects a view to homepage if the user is logged in
class LoginRedirectMixin:
    def dispatch(self, request, *args, **kwargs):
        # redirect to user page if user is already authenticated and is a normal user
        if request.session.get("user_id", None):
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)


# Form for login information validation
# User needs phone number and password to login
class LoginForm(forms.ModelForm):
    password = forms.CharField(max_length=30, required=True)

    class Meta:
        model = SoccerUser
        fields = ['phone_number']

# Form for signup information validation
# User needs first name, last name, phone number and password to login
class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=15, required=True)
    last_name = forms.CharField(max_length=15, required=True)
    password = forms.CharField(max_length=30, required=True)
    confirm_password = forms.CharField(max_length=30, required=True)

    class Meta:
        model = SoccerUser
        fields = ['phone_number']

# Form to reset password
# Reseting password needs phone number and a new confirmed password
class ResetPasswordForm(forms.ModelForm):
    password = forms.CharField(max_length=30, required=True)
    confirm_password = forms.CharField(max_length=30, required=True)

    class Meta:
        model = SoccerUser
        fields = ['phone_number']
    

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
            password = user_info["password"]
            
            try:
                user = SoccerUser.objects.get(phone_number=phone_number)
                django_user = user.user
                # Validate password using Django user object
                if not django_user.check_password(password):
                    request.session['success'] = False
                    request.session['message'] = 'Failed to login. Password is incorrect'
                    return redirect('/login')
            # Throw an exception if there is no existing user with the input phone number
            except SoccerUser.DoesNotExist:
                request.session['success'] = False
                request.session['message'] = 'Failed to login.Phone number is incorrect'
                return redirect('/login')

            # Log the user in by saving user info in the app's session
            request.session['user_id'] = user.id
            request.session['phone_number'] = phone_number
            request.session['name'] = f'{django_user.first_name} {django_user.last_name}'

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

            # Redirect to game page
            return redirect('/game')
        
        # Redirect to login page with an error message (likely never happens due to frontend validation)
        else:
            request.session['success'] = False
            request.session['message'] = 'Failed to login. Please try again'
            return redirect('/login')


# User has to sign up to be able to login
class SignupView(LoginRedirectMixin, TemplateView):
    template_name = 'signup.html'

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
        # Check if the user inputs information correctly
        form = SignupForm(request.POST)
        if form.is_valid():
            user_info = form.cleaned_data
            phone_number = user_info['phone_number']
            password = user_info["password"]
            confirm_password = user_info["confirm_password"]
            first_name = user_info['first_name']
            last_name = user_info['last_name']

            # Check if the passwords match
            if password != confirm_password:
                request.session['success'] = False
                request.session['message'] = "Passwords don't match. Please try again."
                return redirect('/signup')

            # Check if phone_number is unique
            if len(SoccerUser.objects.filter(phone_number=phone_number)) > 0:
                request.session['success'] = False
                request.session['message'] = 'User with this phone number already exists. Please log in.'
                return redirect('/signup')
            
            # Validate password. Password should follow Django standards for passwords
            # If not, the user creation process will fail
            try:
                django_user = User.objects.create_user(
                    username=f'{first_name.lower()}-{last_name.lower()}-{phone_number[7:]}',
                    first_name=first_name, last_name=last_name, password=password)
            except:
                request.session['success'] = False
                request.session['message'] = 'Password is not secure enough. Please try again with a different password.'
                return redirect('/signup')

            # Create a new SoccerUser instance
            user = SoccerUser.objects.create(phone_number=phone_number, user=django_user)

            # Log the user in by saving user info in the app's session
            request.session['user_id'] = user.id
            request.session['phone_number'] = phone_number
            request.session['name'] = f'{django_user.first_name} {django_user.last_name}'

            # Redirect to game page
            return redirect('/game')
                
        # Redirect to signup page with an error message (likely never happens due to frontend validation)
        else:
            request.session['success'] = False
            request.session['message'] = 'Please fill out all the fields'
            return redirect('/signup')

# User can reset password if they forgot they current one
class ResetPasswordView(LoginRedirectMixin, TemplateView):
    template_name = 'reset_password.html'

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
        # Check if the user inputs information correctly
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_info = form.cleaned_data
            phone_number = user_info['phone_number']
            password = user_info["password"]
            confirm_password = user_info["confirm_password"]

            # Check if the passwords match
            if password != confirm_password:
                request.session['success'] = False
                request.session['message'] = "Passwords don't match. Please try again."
                return redirect('/reset_password')

            try:
                user = SoccerUser.objects.get(phone_number=phone_number)
                django_user = user.user
                # Set a new password for this user
                django_user.set_password(password)
                django_user.save()
                request.session['success'] = True
                request.session['message'] = 'Reset password successfully. Please log in with your new password.'
                return redirect('/login')
            # Throw an exception if there is no existing user with the input phone number
            except SoccerUser.DoesNotExist:
                request.session['success'] = False
                request.session['message'] = 'There is no user with this phone number'
                return redirect('/reset_password')

        # Redirect to reset password page with an error message (likely never happens due to frontend validation)
        else:
            request.session['success'] = False
            request.session['message'] = 'Please fill out all the fields properly'
            return redirect('/reset_password') 

# User logout, their user session is deleted but their user information
# is still stored in the database. After logging out user is navigated to the login page
def logout_view(request):
    # Delete user information in the current session
    if 'user_id' in request.session:
        del request.session['user_id']
        del request.session['phone_number']
        del request.session['name']
    return redirect('/login')
