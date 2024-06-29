from django.contrib import admin
from django.urls import path, include
from . import views
from .views import delete_sport
from .views import filtered_sessions, choice

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('admin1', views.admin1, name='admin1'),
    path('player', views.player, name='player'),
    path('organizor', views.organizor, name='organizor'),
    path('mysession', views.mysession, name='mysession'),
    path('joinedsessions', views.joinedsessions, name='joinedsessions'),
    path('cancel_sessions', views.cancel_sessions, name='cancel_sessions'),
    path('change_password', views.change_password, name='change_password'),
    path('report', views.report, name='report'),
    path('signin/', views.signin, name='signin'),
    path('get_sports', views.get_sports, name='get_sports'),
    path('delete_sport/<int:id>/', delete_sport, name='delete_sport'),
    path('createsession/<int:sport_id>/<str:sport_name>/', views.createsession_page, name='createsession'),
    path('create-session/', views.create_session, name='create_session'), 
    # path('recommendation/<str:sport_name>/<int:session_id>/', views.recommendation, name='recommendation'),
    path('filtered_sessions/<int:sport_id>/', views.filtered_sessions, name='filtered_sessions'),
    path('recommendation/<int:sport_id>/', filtered_sessions, name='recommendation'),
    path('choice/', choice, name='all_sports'),  # For displaying all sports
    path('choice/<int:sport_id>/', choice, name='choice'),  # For disp
    
]