from django.shortcuts import render, HttpResponseRedirect, redirect, HttpResponse
from .forms import MeetingCreateForm, MeetingJoinForm
from .models import Meeting
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.contrib import messages
from datetime import datetime, timezone as tz
from django.utils import timezone
import uuid
from django.utils.text import slugify

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('online-meet:home')
    else:
        return render(request, 'login.html')
    return render(request, 'login.html')  

@login_required
def home(request):
    form = MeetingCreateForm()
    if request.method == 'POST':
        form = MeetingCreateForm(request.POST)
        if form.is_valid():
            fm = form.save(commit=False)
            # since in our form, we do not want to be selecting users,
            # we have to set the creator as the current user.
            fm.creator = request.user
            fm.unique_meeting_name = slugify(
                str(form.cleaned_data['title_of_meeting']) + '-' + str(uuid.uuid4().hex[:6].upper())
            )
            fm.save()
            unique_meeting_name = fm.unique_meeting_name
            return HttpResponseRedirect(reverse('online-meet:meeting',kwargs={'unique_meeting_name': unique_meeting_name}))
    return render(request, 'onlinemeet/home.html', {'form': form})


@login_required()  # to ensure only logged in user can view this page.
def meeting_list(request):
    """We are going to filter the meeting, so only the registered user can view
    the page, and then all meeting created by such individual will be displayed"""
    user = request.user
    # meeting_url = request.build_absolute_uri()
    meetings = Meeting.objects.filter(creator=user)

    return render(request, 'onlinemeet/meeting_list.html', {'meetings': meetings})

@login_required
def join_meeting(request):
    form = MeetingJoinForm()
    if request.method == 'POST':
        form = MeetingJoinForm(request.POST)
        if form.is_valid():
            unique_meeting_name = form.cleaned_data['unique_meeting_name']
            if Meeting.objects.filter(unique_meeting_name=unique_meeting_name).exists():
                return HttpResponseRedirect(reverse('online-meet:meeting', kwargs={'unique_meeting_name':unique_meeting_name}))
            return HttpResponse(f'Meeting name {unique_meeting_name} doesnot exits')
    return render(request, 'onlinemeet/join_meeting.html', {'form': form})

@login_required
def meeting(request, unique_meeting_name):
    message = None
    if not unique_meeting_name:
        return HttpResponse(f"No any meeting is running with the meeting code: {unique_meeting_name}")
    try:
        meeting = Meeting.objects.get(unique_meeting_name=unique_meeting_name)
    except:
        return HttpResponse(f"No any meeting is running with the meeting code: {unique_meeting_name}")

    if not meeting.meeting_time:
        """
        will check if it is not time for the meeting using the property we declared in the model.
        """
        now = timezone.localtime()
        t = abs(now - meeting.starting_date_time).total_seconds()
        MinutesGet, SecondsGet = divmod(t, 60)
        HoursGet, MinutesGet = divmod(MinutesGet, 60)

        message = f"it is not the time for meeting {meeting.title_of_meeting}, Meeting starts in {HoursGet} Hours : {MinutesGet} Minutes : {'{:.2f}'.format(SecondsGet)} Seconds."
        # return render(request, 'onlinemeet/meeting_list.html', {'meetings': meetings})
        print(now, message)

        messages.warning(request, message)
        # return render(request, 'onlinemeet/meeting_list.html', {'meetings': meetings})
        return HttpResponseRedirect(reverse('online-meet:home'))
    
    # elif meeting.after_meeting:
    #     """ will check if the meeting time has passed"""
    #     now = timezone.localtime()
    #     t = abs(meeting.ending_date_time - now).total_seconds()
    #     MinutesGet, SecondsGet = divmod(t, 60)
    #     HoursGet, MinutesGet = divmod(MinutesGet, 60)

    #     message = f"The meeting {meeting.title_of_meeting}, ended {HoursGet} Hours : {MinutesGet} Minutes : {'{:.2f}'.format(SecondsGet)} Seconds."
    #     print(now, message)
    #     messages.warning(request, message)
    #     return HttpResponseRedirect(reverse('online-meet:home'))


    if request.user != meeting.creator:
        """check to know if the current user is the creator of the meeting
        if True, then the person will be redirected to a page that has moderator privileges, else, redirect the guest to the guest page."""
        return render(request, 'onlinemeet/guest.html', {'meeting': meeting,
        "message": message})

    return render(request, 'onlinemeet/meeting_page.html', {'meeting': meeting})


