from cmath import e
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from Sports_Guide import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Sport
from .forms import SportForm 
from .models import Session
# from .forms import SessionForm
from django.utils import timezone
from django.shortcuts import get_object_or_404
# Create your views here.
def home(request):
    return render(request, "authentication/index.html")
@login_required
def player(request):
      csports = Sport.objects.all()
      sessions = Session.objects.all()
      return render(request, 'Player.html', {'csports': csports , 'sessions': sessions})

@login_required
def admin1(request):
    return render(request, "admin1.html")
@login_required
def organizor(request):
     csports = Sport.objects.all()
     return render(request, 'organizor.html', {'csports': csports})
# @login_required
# def mysession(request):
#     return render(request, "mysession.html")
@login_required
def joinedsessions(request):
    return render(request, "joinedsessions.html")
@login_required
def cancel_sessions(request):
    return render(request, "cancel_sessions.html")
@login_required
def change_password(request):
    return render(request, "change_password.html")
@login_required
def report(request):
    return render(request, "report.html")

def signup(request):
    if request.method == "POST":
        try:
            username = request.POST['username']
            fname = request.POST['fname']
            lname = request.POST['lname']
            email = request.POST['email']
            pass1 = request.POST['pass1']
            pass2 = request.POST['pass2']
            
            if User.objects.filter(username=username).exists():
                raise ValidationError("Username already exists! Please try some other username.")
            
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email Already Registered!!")
            
            if len(username) > 20:
                raise ValidationError("Username must be under 20 characters!!")
            
            if pass1 != pass2:
                raise ValidationError("Passwords didn't match!!")
            
            if not username.isalnum():
                raise ValidationError("Username must be Alpha-Numeric!!")
            
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.is_active = False
            myuser.save()
            
            messages.success(request, "Your Account has been created successfully!! Please check your email to confirm your email address in order to activate your account.")
            
            # Welcome Email
            subject = "Welcome to Sport Guide"
            message = "Hello " + myuser.first_name + "!! \n" + "Welcome to Sport Guide \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nSport Guide Team"        
            from_email = settings.EMAIL_HOST_USER
            to_list = [myuser.email]
            send_mail(subject, message, from_email, to_list, fail_silently=False)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email @ Sport Guide Login!!"
            message2 = render_to_string('email_confirmation.html', {
                'name': myuser.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
                'token': generate_token.make_token(myuser)
            })
            email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email])
            email.fail_silently = True
            email.send()
            
            return redirect('signin')
        
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect('home')
        
        except IntegrityError as e:
            messages.error(request, "An error occurred while processing your request. Please try again later.")
            return redirect('home')
    
    return render(request, "authentication/signup.html")

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        if user is not None:
            if user.is_staff:  # Checking if the user is an admin
                login(request, user)
                messages.success(request, "Logged In Successfully as Admin!!")
                return redirect('admin1')  # Redirect admin to admin dashboard
            else:
                login(request, user)
                messages.error(request, "Logged In Successfully as Player!!")
                return redirect('admin1')  # Redirect regular users to home page
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('signin')

def get_sports(request):
    if request.method == "POST":
        id = request.POST.get('id')
        sport_name = request.POST.get('sport_name')
        print(id , sport_name)
        ins = Sport(id=id, sport_name=sport_name)
        ins.save()
        print("The Sport is save into the DB")
        csports = Sport.objects.all()
        messages.success(request, "Sport create successfully")
        return render(request, 'organizor.html' ,{'csports': csports})
    else:
        csports = Sport.objects.all()
        return render(request, 'organizor.html', {'csports': csports})

from django.http import JsonResponse

def delete_sport(request, sport_id):
    try:
        sport = Sport.objects.get(id=sport_id)
        sport.delete()
        return JsonResponse({'message': 'Sport deleted successfully'}, status=200)
    except Sport.DoesNotExist:
        return JsonResponse({'error': 'Sport not found'}, status=404)

# from django.shortcuts import get_object_or_404

# def delete_sport(request, sport_id):
#     # Assuming Todo is the model name and 'todo_id' is the parameter
#     sport = get_object_or_404(Sport, pk=sport_id)
#     sport.delete()
#     # Redirect to a page where you want to go after deletion
#     return redirect('organizor')  # Redirecting to a hypothetical todo list view

def delete_sport(request, id):
    if request.method == 'POST':
        sport = Sport.objects.get(pk=id)
        sport.delete()
        messages.success(request, "Sport deleted successfully")
        return redirect('get_sports')
    else:
        messages.error(request, "Invalid request method")
        return redirect('get_sports')
    
def createsession_page(request, sport_id,sport_name):
    # Logic to render the recommendation page
    return render(request, 'createsession.html',  {'sport_id': sport_id, 'sport_name':sport_name})    

def create_session(request):
    if request.method == 'POST':
        venue = request.POST.get('venue')
        number_of_teams = request.POST.get('numberofTeams')
        time = request.POST.get('time')
        sport_name = request.POST.get('sport_name')

        # Save session data to the database
        session = Session.objects.create(
            sport_name=sport_name,
            venue=venue,
            number_of_teams=number_of_teams,
            time=time
        )
        return redirect('recommendation', sport_name=sport_name, session_id=session.id)

    return render(request, 'createsession.html')

def recommendation(request,sport_name,session_id):
    # Retrieve all sessions from the database
    sessions = Session.objects.all()
    # session_teams_range = range(1, sessions.number_of_teams + 1)

    # Pass the retrieved sessions to the recommendation.html template
    return render(request, 'recommendation.html', {'sessions': sessions})
def mysession(request):
    sessions=Session.objects.all()
    return render(request,'mysession.html', {'sessions': sessions})


def filtered_sessions(request, sport_id):
    try:
        sport = Sport.objects.get(id=sport_id)
        sessions = Session.objects.filter(sport_name=sport.sport_name)
        return render(request, 'filtered_sessions.html', {'sessions': sessions})
    except Sport.DoesNotExist:
        return render(request, 'filtered_sessions.html', {'sessions': None})

import logging    
logger = logging.getLogger(__name__)    
    
def choice(request, sport_id=None):
    try:
        if sport_id is not None:
            session = get_object_or_404(Session, pk=sport_id)
            session.team_range = range(1, session.number_of_teams + 1)
            return render(request, "choice.html", {"session": session})
        else:
            logger.error("No sport_id provided in URL")
            return render(request, "choice.html", {"session": None})
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        return render(request, "choice.html", {"session": None})