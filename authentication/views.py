from cmath import e
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from geeksforgeeks import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")
def player(request):
    return render(request, "Player.html")
def admin1(request):
    return render(request, "admin1.html")
def organizor(request):
    return render(request, "organizor.html")
def mysession(request):
    return render(request, "mysession.html")
def joinedsessions(request):
    return render(request, "joinedsessions.html")
def cancel_sessions(request):
    return render(request, "cancel_sessions.html")
def change_password(request):
    return render(request, "change_password.html")
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
                messages.error(request, "Logged In Successfully as Player!!")
                return redirect('admin1')  # Redirect regular users to home page
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')