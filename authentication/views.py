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
from .models import Sport, Session, Player, PlayerStats, PlayerType, Team, Match, TeamComposition
from .forms import SportForm
from django.utils import timezone
import logging
import json
from django.views.decorators.http import require_http_methods

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

def sports(request):
    return render(request, "authentication/sports.html")

def contact(request):
    return render(request, "authentication/contact.html")

def about(request):
    return render(request, "authentication/about.html")


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
            
            # Store session ID in the session
            request.session['session_id'] = session.id
            
            # Get recommended players
            recommended_players = []
            try:
                # First try to get players from Player_reco model
                players = Player_reco.objects.all()
                for player in players:
                    recommended_players.append({
                        'name': player.name,
                        'role': player.role
                    })
            except:
                # If that fails, use some default players
                recommended_players = [
                    {'name': 'Het Maheta', 'role': 'batsman'},
                    {'name': 'Jaimin Patel', 'role': 'batsman'},
                    {'name': 'Nil Patel', 'role': 'batsman'},
                    {'name': 'Yash', 'role': 'bowler'},
                    {'name': 'Yash Joshi', 'role': 'bowler'},
                    {'name': 'hello', 'role': 'allrounder'},
                    {'name': 'postgres', 'role': 'allrounder'}
                ]
            
            return render(request, "choice.html", {
                "session": session,
                "recommended_players": recommended_players
            })
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



from rest_framework import viewsets
from .models import Player_reco, PlayerStats
from .serializers import PlayerSerializer, PlayerStatsSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player_reco.objects.all()
    serializer_class = PlayerSerializer

class PlayerStatsViewSet(viewsets.ModelViewSet):
    queryset = PlayerStats.objects.all()
    serializer_class = PlayerStatsSerializer

from django.http import JsonResponse
from authentication.ai import train_model, predict_winning_probability
from authentication.models import Player_reco

def recommend_players(request):
    try:
        # Use the AI model to get recommendations
        model = train_model()
        if model is None:
            return JsonResponse({"error": "Not enough player data"})

        # Get top 11 players from the model
        top_players = model.classes_[:11]

        # Get player details from the Player model
        player_data = []
        for player_name in top_players:
            try:
                # Get all players with this name and use the first one
                players = Player.objects.filter(name=player_name)
                if players.exists():
                    player = players.first()
                    # Determine role based on player_type
                    role = 'allrounder'  # default role
                    if player.player_type:
                        player_type_name = player.player_type.name.lower()
                        if 'bat' in player_type_name:
                            role = 'batsman'
                        elif 'bowl' in player_type_name:
                            role = 'bowler'
                        else:
                            role = 'allrounder'
                    
                    player_data.append({
                        "name": player.name,
                        "role": role
                    })
                else:
                    # If player not found, try to get from Player_reco model
                    player_reco = Player_reco.objects.filter(name=player_name).first()
                    if player_reco:
                        player_data.append({
                            "name": player_reco.name,
                            "role": player_reco.role
                        })
                    else:
                        # If not found in either model, add as all-rounder
                        player_data.append({
                            "name": player_name,
                            "role": "allrounder"
                        })
            except Exception as e:
                print(f"Error processing player {player_name}: {str(e)}")
                # Add as all-rounder in case of any error
                player_data.append({
                    "name": player_name,
                    "role": "allrounder"
                })

        print("Recommended players:", player_data)  # Debug print
        return JsonResponse({"recommended_players": player_data})
    except Exception as e:
        print("Error in recommend_players:", str(e))  # Debug print
        return JsonResponse({"error": str(e)})

def predict_match(request, team1, team2):
    result = predict_winning_probability(team1, team2)
    return JsonResponse(result)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from authentication.models import Player, PlayerStats
from authentication.serializers import PlayerSerializer, PlayerStatsSerializer

@api_view(['POST'])
def store_player_data(request):
    data = request.data

    # Create or update Player
    player, created = Player.objects.get_or_create(
        name=data.get("name"),
        defaults={"role": data.get("role"), "team": data.get("team")}
    )

    # Create or update Player Stats
    PlayerStats.objects.update_or_create(
        player=player,
        defaults={
            "batting_average": data.get("batting_average", 0.0),
            "strike_rate": data.get("strike_rate", 0.0),
            "total_runs": data.get("total_runs", 0),
            "wickets": data.get("wickets", 0),
            "bowling_average": data.get("bowling_average", 0.0),
            "economy": data.get("economy", 0.0),
            "matches_played": data.get("matches_played", 0),
            "highest_score": data.get("highest_score", 0),
            "best_bowling_figures": data.get("best_bowling_figures", ""),
        }
    )

    return Response({"message": "Player data stored successfully!"})

#data upload

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Player_reco, PlayerStats
from .serializers import PlayerSerializer, PlayerStatsSerializer

class UploadPlayersView(APIView):
    def post(self, request):
        players_data = request.data.get("players_reco", [])  # Get players from JSON

        for player_data in players_data:
            player, created = Player.objects.get_or_create(
                name=player_data["name"],
                defaults={
                    "role": player_data["role"],
                    "team": player_data.get("team", ""),
                    "age": player_data.get("age", 18),
                    "nationality": player_data.get("nationality", "Unknown"),
                }
            )

            # Store or update player stats
            PlayerStats.objects.update_or_create(
                player=player,
                defaults={
                    "batting_average": player_data.get("batting_average", 0.0),
                    "strike_rate": player_data.get("strike_rate", 0.0),
                    "total_runs": player_data.get("total_runs", 0),
                    "wickets": player_data.get("wickets", 0),
                    "bowling_average": player_data.get("bowling_average", 0.0),
                    "economy": player_data.get("economy", 0.0),
                    "matches_played": player_data.get("matches_played", 0),
                    "highest_score": player_data.get("highest_score", 0),
                    "best_bowling_figures": player_data.get("best_bowling_figures", ""),
                }
            )
        data = players_data.get("players_reco")
        print(data)
        return Response({"message": "Players stored successfully!"}, status=status.HTTP_201_CREATED)

def create_player_form(request):
    player_types = PlayerType.objects.all()
    return render(request, 'authentication/create_player.html', {'player_types': player_types})

def create_player(request):
    if request.method == 'POST':
        try:
            # Create Player instance
            player = Player.objects.create(
                name=request.POST['name'],
                player_type_id=request.POST['player_type']
            )

            # Create PlayerStats instance
            PlayerStats.objects.create(
                player=player,
                batting_average=float(request.POST['batting_average']),
                strike_rate=float(request.POST['strike_rate']),
                total_runs=int(request.POST['total_runs']),
                wickets=int(request.POST['wickets']),
                bowling_average=float(request.POST['bowling_average']),
                economy=float(request.POST['economy']),
                recent_form=float(request.POST['recent_form']),
                fitness_level=float(request.POST['fitness_level']),
                match_experience=int(request.POST['match_experience'])
            )
            
            messages.success(request, 'Player created successfully!')
            return redirect('create_player_form')
        except Exception as e:
            messages.error(request, f'Error creating player: {str(e)}')
            return redirect('create_player_form')
    
    return redirect('create_player_form')

@login_required
def get_player_stats(request, player_name):
    try:
        # Decode the URL-encoded player name
        player_name = player_name.replace('%20', ' ')
        print(f"Looking up stats for player: {player_name}")
        
        # Try to get the player and their stats
        player = Player.objects.filter(name=player_name).first()
        if not player:
            print(f"Player not found: {player_name}")
            return JsonResponse({
                "error": f"Player '{player_name}' not found in database",
                "available_players": list(Player.objects.values_list('name', flat=True))
            }, status=404)
            
        stats = PlayerStats.objects.filter(player=player).first()
        if not stats:
            print(f"Stats not found for player: {player_name}")
            return JsonResponse({
                "error": f"Statistics not found for player '{player_name}'"
            }, status=404)
            
        print(f"Found stats for player {player_name}: {stats}")
        
        # Format the stats as a dictionary
        stats_data = {
            "stats": {
                "batting_average": float(stats.batting_average) if stats.batting_average is not None else None,
                "strike_rate": float(stats.strike_rate) if stats.strike_rate is not None else None,
                "total_runs": stats.total_runs,
                "wickets": stats.wickets,
                "bowling_average": float(stats.bowling_average) if stats.bowling_average is not None else None,
                "economy": float(stats.economy) if stats.economy is not None else None,
                "matches_played": stats.matches_played,
                "highest_score": stats.highest_score,
                "best_bowling_figures": stats.best_bowling_figures if hasattr(stats, 'best_bowling_figures') else None,
            }
        }
        return JsonResponse(stats_data)
    except Exception as e:
        print(f"Error getting stats for {player_name}: {str(e)}")
        return JsonResponse({
            "error": f"Error retrieving player statistics: {str(e)}"
        }, status=500)

@login_required
@require_http_methods(["POST"])
def save_teams(request):
    try:
        data = json.loads(request.body)
        session = Session.objects.get(id=request.session.get('session_id'))
        teams_data = data.get('teams', {})
        
        # Check for duplicate team names in the database for this session
        team_names = [team_data['name'] for team_data in teams_data.values()]
        existing_teams = Team.objects.filter(session=session, name__in=team_names)
        if existing_teams.exists():
            return JsonResponse({
                'status': 'error',
                'message': f'Teams with names {", ".join(t.name for t in existing_teams)} already exist in this session'
            }, status=400)

        # Store all players to check for duplicates
        all_players = []
        for team_data in teams_data.values():
            all_players.extend(team_data['players'])
        if len(all_players) != len(set(all_players)):
            return JsonResponse({
                'status': 'error',
                'message': 'Duplicate players found across teams'
            }, status=400)

        # Create teams and save players
        created_teams = []
        for team_data in teams_data.values():
            # Create the team
            team = Team.objects.create(
                session=session,
                name=team_data['name']
            )
            
            # Add players to the team
            for player_name in team_data['players']:
                player, created = Player.objects.get_or_create(
                    name=player_name,
                    defaults={'player_type': PlayerType.objects.get_or_create(name='Unknown')[0]}
                )
                team.players.add(player)
            
            created_teams.append(team)

        # Create match records for team combinations if there are exactly 2 teams
        if len(created_teams) == 2:
            match = Match.objects.create(
                session=session,
                team1=created_teams[0],
                team2=created_teams[1],
                date=timezone.now()
            )

            # Create team compositions
            TeamComposition.objects.create(
                team=created_teams[0],
                match=match,
                is_team1=True
            ).players.set(created_teams[0].players.all())

            TeamComposition.objects.create(
                team=created_teams[1],
                match=match,
                is_team1=False
            ).players.set(created_teams[1].players.all())

        return JsonResponse({
            'status': 'success',
            'message': 'Teams saved successfully',
            'teams': [{
                'id': team.id,
                'name': team.name,
                'player_count': team.players.count()
            } for team in created_teams]
        })
    except Session.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
