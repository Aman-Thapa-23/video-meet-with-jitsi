from django import forms
from .models import Meeting


class DateTimePickerInput(forms.DateTimeInput):
    input_type= 'datetime-local'
    input_formats=['%m/%d/%y %H:%M %p']

class MeetingCreateForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["title_of_meeting", "starting_date_time"]

        widgets = {
            'starting_date_time': DateTimePickerInput(),
        }

class MeetingJoinForm(forms.Form):
    unique_meeting_name = forms.CharField(max_length=20)

    class Meta:
        fields = ['unique_meeting_name']
