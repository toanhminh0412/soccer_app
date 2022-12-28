import os
import random
import string
from twilio.rest import Client

from django.views.generic import TemplateView
from django import forms
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.models import User

from soccer.models import SoccerUser, Game

# Enable the line below if need to specify the path of .env file
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Get access information for Twilio
account_sid = os.environ.get('TWILIO_ACCOUNT_SID', None)
auth_token = os.environ.get('TWILIO_AUTH_TOKEN', None)


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
    confirm_password = forms.CharField(max_length=30, required=False)
    confirmation_code = forms.CharField(max_length=10, required=False)

    class Meta:
        model = SoccerUser
        fields = ['phone_number']

# Form to reset password
# Reseting password needs phone number and a new confirmed password
class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)
    phone_number = forms.CharField(max_length=10, required=False)
    confirmation_code = forms.CharField(max_length=10, required=False)

    # class Meta:
    #     model = SoccerUser
    #     fields = ['phone_number']
    

# User must login to the application to use app's features
class LoginView(LoginRedirectMixin, TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Display message if any
        context['success'] = self.request.session.get('success', None)
        context['message'] = self.request.session.get('message', None)
        
        # Clear message in session if exists
        # if 'success' in self.request.session:
        #     del self.request.session['success']
        # if 'message' in self.request.session:
        #     del self.request.session['message']
        # if 'signup_confirmation_code' in self.request.session:
        #     del self.request.session['signup_confirmation_code']
        self.request.session.clear()
        
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
                request.session['message'] = 'Failed to login. Phone number is incorrect'
                return redirect('/login')

            # Log the user in by saving user info in the app's session
            request.session['user_id'] = user.id
            request.session['phone_number'] = phone_number
            request.session['name'] = f'{django_user.first_name} {django_user.last_name}'

            # Remove all games in the past
            for game in Game.objects.all():
                if game.date < timezone.now():
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

        # If these have values, that means user is typing in confirmation code
        # These values will be rendered invisibly in the confirmation code form
        context['signup_phone_number'] = self.request.session.get('signup_phone_number', None)
        context['signup_password'] = self.request.session.get('signup_password', None)
        context['signup_first_name'] = self.request.session.get('signup_first_name', None)
        context['signup_last_name'] = self.request.session.get('signup_last_name', None)
        context['signup_confirmation_code'] = self.request.session.get('signup_confirmation_code', None)

        # Clear message in session if exists
        if 'success' in self.request.session:
            del self.request.session['success']
        if 'message' in self.request.session:
            del self.request.session['message']
        if 'signup_phone_number' in self.request.session:
            del self.request.session['signup_phone_number']
        if 'signup_password' in self.request.session:
            del self.request.session['signup_password']
        if 'signup_first_name' in self.request.session:
            del self.request.session['signup_first_name']
        if 'signup_last_name' in self.request.session:
            del self.request.session['signup_last_name']
        if 'reset_password_confirmation_code' in self.request.session:
            del self.request.session['reset_password_confirmation_code']
        
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
            confirmation_code = user_info['confirmation_code']
            
            if not confirmation_code:
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
                        first_name=first_name, last_name=last_name, password=password
                    )
                    django_user.delete()
                except:
                    request.session['success'] = False
                    request.session['message'] = 'Password is not secure enough. Please try again with a different password.'
                    return redirect('/signup')

                # Save information of the new user to session
                request.session['signup_phone_number'] = phone_number
                request.session['signup_password'] = password
                request.session['signup_first_name'] = first_name
                request.session['signup_last_name'] = last_name

                # Generate a random code of length 10 to send to user
                letters = string.ascii_lowercase
                random_code = ''.join(random.choice(letters) for i in range(10))

                # Send the code to phone number
                client = Client(account_sid, auth_token)
                message = client.messages\
                    .create(
                        body=f"Here is the confirmation code for Victoria Soccer App: {random_code}.\
                                Have a nice day.",
                        from_='+1 236 303 5408',
                        to=f'+1{phone_number}'
                    )
                print(message.sid)

                # Save the code to the model for later comparison
                request.session['signup_confirmation_code'] = random_code
                return redirect('/signup')

            # Confirmation code is correct
            if confirmation_code == self.request.session['signup_confirmation_code']:
                del request.session['signup_confirmation_code']
                # Create a new SoccerUser instance
                django_user = User.objects.create_user(
                    username=f'{first_name.lower()}-{last_name.lower()}-{phone_number[7:]}',
                    first_name=first_name, last_name=last_name, password=password
                )

                # Create a new SoccerUser instance
                user = SoccerUser.objects.create(phone_number=phone_number, user=django_user)
                
                # Log the user in by saving user info in the app's session
                request.session['user_id'] = user.id
                request.session['phone_number'] = phone_number
                request.session['name'] = f'{django_user.first_name} {django_user.last_name}'

                # Redirect to game page
                return redirect('/game')
            
            # Confirmation code is incorrect
            # Flash an error message and ask user to retype the code
            request.session['signup_phone_number'] = phone_number
            request.session['signup_password'] = password
            request.session['signup_first_name'] = first_name
            request.session['signup_last_name'] = last_name
            request.session['success'] = False
            request.session['message'] = 'Confirmation code is not correct. Please retype the code.'
            return redirect('/signup')
                
        # Redirect to signup page with an error message (likely never happens due to frontend validation)
        else:
            request.session['success'] = False
            request.session['message'] = 'Please fill out all the fields properly'
            return redirect('/signup')


# User can reset password if they forgot they current one
class ResetPasswordView(LoginRedirectMixin, TemplateView):
    template_name = 'reset_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Display message if any
        context['success'] = self.request.session.get('success', None)
        context['message'] = self.request.session.get('message', None)

        # Ask user for phone number before asking for a new password
        # This is to send a confirmation code to verify user owns this phone number
        # The values of the two fields below indicate the followings:
        # - None/False: Phone number has not been sent. Render a textbox for user to input their phone number
        # - Phone number/False: Phone number has not been verified but a confirmation code is sent.
        # Render a text box for user to type in the confirmation code 
        # - Phone number/True: Phone number has been verified. Render two fields for user to type in their new password and confirm it.
        context['reset_password_phone_number'] = self.request.session.get('reset_password_phone_number', None)
        context['phone_number_verified'] = self.request.session.get('phone_number_verified', False)
        
        # Clear message in session if exists
        if 'success' in self.request.session:
            del self.request.session['success']
        if 'message' in self.request.session:
            del self.request.session['message']
        if 'reset_password_phone_number' in self.request.session:
            del self.request.session['reset_password_phone_number']
        if 'phone_number_verified' in self.request.session:
            del self.request.session['phone_number_verified']
        if 'signup_confirmation_code' in self.request.session:
            del self.request.session['signup_confirmation_code']
        
        return context

    def post(self, request, **kwargs):
        # Check if the user inputs information correctly
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_info = form.cleaned_data
            phone_number = user_info['phone_number']
            password = user_info["password"]
            confirm_password = user_info["confirm_password"]
            confirmation_code = user_info["confirmation_code"]
            
            # If user submit a phone number, send a message to that phone number
            # to verify this user owns the phone number
            if phone_number and not password and not confirmation_code:
                try:
                    user = SoccerUser.objects.get(phone_number=phone_number)
                    # Generate a random code of length 10 to send to user
                    letters = string.ascii_lowercase
                    random_code = ''.join(random.choice(letters) for i in range(10))

                    # Get the code to phone number
                    client = Client(account_sid, auth_token)
                    message = client.messages\
                        .create(
                            body=f"Here is the confirmation code for Victoria Soccer App: {random_code}.\
                                 Have a nice day.",
                            from_='+1 236 303 5408',
                            to=f'+1{phone_number}'
                        )
                    print(message.sid)

                    # Save the code to the session for later comparison
                    request.session['reset_password_confirmation_code'] = random_code

                    # Ask user to type in the code
                    request.session['reset_password_phone_number'] = phone_number
                    request.session['phone_number_verified'] = False
                    return redirect('/reset_password')
                # Throw an exception if there is no existing user with the input phone number
                except SoccerUser.DoesNotExist:
                    request.session['success'] = False
                    request.session['message'] = 'There is no user with this phone number. Please sign up.'
                    return redirect('/reset_password')
            
            # After user receive a message with a confirmation code, user type that code
            # in to verify their phone number
            elif phone_number and confirmation_code and not password:
                user = SoccerUser.objects.get(phone_number=phone_number)
                # Ask user to try again if the confirmation code is incorrect
                if confirmation_code != request.session['reset_password_confirmation_code']:
                    request.session['reset_password_phone_number'] = phone_number
                    request.session['phone_number_verified'] = False
                    request.session['success'] = False
                    request.session['message'] = 'Confirmation code is not correct. Please try again.'
                    return redirect('/reset_password')
                # Ask user to type in a new password if the confirmation code is correct
                else:
                    request.session['success'] = True
                    request.session['message'] = 'Confirmation code is correct. Please type in your new password.'
                    request.session['reset_password_phone_number'] = phone_number
                    request.session['phone_number_verified'] = True
                    del request.session['reset_password_confirmation_code']
                    return redirect('/reset_password')
            
            # User verified their phone number and type in their new password
            else:
                user = SoccerUser.objects.get(phone_number=phone_number)

                # Check if the passwords match. If not flash a message and ask for
                # password input again
                if password != confirm_password:
                    request.session['reset_password_phone_number'] = phone_number
                    request.session['phone_number_verified'] = True
                    request.session['success'] = False
                    request.session['message'] = "Passwords don't match. Please try again."
                    return redirect('/reset_password')

                django_user = user.user
                # Set a new password for this user
                try:
                    django_user.set_password(password)
                    django_user.save()
                except:
                    request.session['reset_password_phone_number'] = phone_number
                    request.session['phone_number_verified'] = True
                    request.session['success'] = False
                    request.session['message'] = "Passwords is not secure enough. Please type in another password."
                    return redirect('/reset_password')

                # Render a success message and redirect to login page
                request.session['success'] = True
                request.session['message'] = 'Reset password successfully. Please log in with your new password.'
                return redirect('/login')

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
