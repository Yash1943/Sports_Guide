from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from Sports_Guide import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from .tokens import generate_token
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import Sport, Session
from .forms import SportForm
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in to access this page.")
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def home(request):
    return render(request, "authentication/index.html")

def sports_homePage(request):
    return redirect(request,"sports.html")

@login_required
def player(request):
    csports = Sport.objects.all()
    sessions = Session.objects.all()
    return render(request, 'Player.html', {'csports': csports, 'sessions': sessions})

@login_required
def admin1(request):
    return render(request, "admin1.html")



def about_view(request):
    return redirect(request,"authentication/about.html")

def contact_view(request):
    return redirect(request,"authentication/contact.html")

@login_required
def organizor(request):
    csports = Sport.objects.all()
    return render(request, 'organizor.html', {'csports': csports})

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
            return redirect('signup')

        except IntegrityError as e:
            messages.error(request, "An error occurred while processing your request. Please try again later.")
            return redirect('signup')

    return render(request, "authentication/signup.html")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, "Logged In Successfully as Admin!!")
                return redirect('admin1')
            else:
                login(request, user)
                messages.success(request, "Logged In Successfully as Player!!")
                return redirect('player')
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('signin')
    return render(request, "authentication/signin.html")

@login_required
def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('signin')

@login_required
def get_sports(request):
    if request.method == "POST":
        id = request.POST.get('id')
        sport_name = request.POST.get('sport_name')
        print(id, sport_name)
        ins = Sport(id=id, sport_name=sport_name)
        ins.save()
        print("The Sport is saved into the DB")
        csports = Sport.objects.all()
        messages.success(request, "Sport created successfully")
        return render(request, 'organizor.html', {'csports': csports})
    else:
        csports = Sport.objects.all()
        return render(request, 'organizor.html', {'csports': csports})

@login_required
def delete_sport(request, sport_id):
    try:
        sport = Sport.objects.get(id=sport_id)
        sport.delete()
        return JsonResponse({'message': 'Sport deleted successfully'}, status=200)
    except Sport.DoesNotExist:
        return JsonResponse({'error': 'Sport not found'}, status=404)

@login_required
def delete_sport(request, id):
    if request.method == 'POST':
        sport = Sport.objects.get(pk=id)
        sport.delete()
        messages.success(request, "Sport deleted successfully")
        return redirect('get_sports')
    else:
        messages.error(request, "Invalid request method")
        return redirect('get_sports')

@login_required
def createsession_page(request, sport_id, sport_name):
    return render(request, 'createsession.html', {'sport_id': sport_id, 'sport_name': sport_name})

@login_required
def create_session(request):
    if request.method == 'POST':
        venue = request.POST.get('venue')
        number_of_teams = request.POST.get('numberofTeams')
        time = request.POST.get('time')
        sport_name = request.POST.get('sport_name')

        session = Session.objects.create(
            sport_name=sport_name,
            venue=venue,
            number_of_teams=number_of_teams,
            time=time
        )
        return redirect('recommendation', sport_name=sport_name, session_id=session.id)

    return render(request, 'createsession.html')

@login_required
def recommendation(request, sport_name, session_id):
    sessions = Session.objects.all()
    return render(request, 'recommendation.html', {'sessions': sessions})

@login_required
def mysession(request):
    sessions = Session.objects.all()
    return render(request, 'mysession.html', {'sessions': sessions})

@login_required
def filtered_sessions(request, sport_id):
    try:
        sport = Sport.objects.get(id=sport_id)
        sessions = Session.objects.filter(sport_name=sport.sport_name)
        return render(request, 'filtered_sessions.html', {'sessions': sessions})
    except Sport.DoesNotExist:
        return render(request, 'filtered_sessions.html', {'sessions': None})

@login_required
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

from .models import Team, PlayerType, Player, Session

def save_team(request, session_id):
    if request.method == 'POST':
        session = Session.objects.get(id=session_id)
        team_data = request.POST.dict()
        
        # Loop through the posted data to create teams
        for i in range(1, int(team_data['number_of_teams']) + 1):
            team_name = team_data.get(f'team{i}Name')
            player_type_name = team_data.get(f'team{i}PlayerType')

            # Get or create the PlayerType
            player_type, created = PlayerType.objects.get_or_create(name=player_type_name)

            # Create the Team
            team = Team.objects.create(name=team_name, session=session)

            # Add players to the team based on player type
            player_names = team_data.getlist(f'team{i}Players')
            for player_name in player_names:
                # Get or create the Player
                player, created = Player.objects.get_or_create(name=player_name, player_type=player_type)
                team.players.add(player)
        
        return redirect('team_list')  # Redirect to a list of teams or another view after saving

    # Handle GET request (render form)
    session = Session.objects.get(id=session_id)
    context = {
        'session': session,
    }
    return render(request, 'team_selection.html', context)