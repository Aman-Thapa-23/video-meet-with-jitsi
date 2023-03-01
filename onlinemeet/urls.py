from django.urls import path
from . import views

app_name = 'online-meet'

urlpatterns = [
    path('', views.home, name='home'),
    path('join/', views.join_meeting, name='join-meet'),
    path('my-meetings/', views.meeting_list, name='meeting_list'),
    path('live-meeting/<unique_meeting_name>/', views.meeting, name='meeting'),

]