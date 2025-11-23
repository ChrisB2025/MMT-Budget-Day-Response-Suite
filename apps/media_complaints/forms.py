"""Forms for media complaint submission"""
from django import forms
from .models import Complaint, MediaOutlet


class ComplaintForm(forms.ModelForm):
    """Form for submitting a media complaint"""

    class Meta:
        model = Complaint
        fields = [
            'outlet',
            'incident_date',
            'programme_name',
            'presenter_journalist',
            'timestamp',
            'claim_description',
            'context',
            'severity',
            'preferred_tone'
        ]
        widgets = {
            'outlet': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }),
            'incident_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }),
            'programme_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'e.g., News at Ten, The Daily Mail, etc.'
            }),
            'presenter_journalist': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'Optional'
            }),
            'timestamp': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'e.g., 14:23 or 2:23 PM (optional)'
            }),
            'claim_description': forms.Textarea(attrs={
                'rows': 5,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'Describe the misinformation or misleading claim...'
            }),
            'context': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                'placeholder': 'Any additional context that would be helpful... (optional)'
            }),
            'severity': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }),
            'preferred_tone': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent'
            }),
        }
        help_texts = {
            'outlet': 'Select the media outlet where the misinformation appeared',
            'incident_date': 'Date when the misinformation was broadcast/published',
            'programme_name': 'Name of the TV/radio show, or article headline',
            'presenter_journalist': 'Name of the person who made the claim (if known)',
            'timestamp': 'Approximate time during the programme (if applicable)',
            'claim_description': 'Describe the misleading claim in detail',
            'context': 'Any additional information that would help understand the situation',
            'severity': 'How serious do you think this misinformation is?',
            'preferred_tone': 'What tone should the complaint letter use?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active outlets
        self.fields['outlet'].queryset = MediaOutlet.objects.filter(is_active=True)

        # Make some fields optional
        self.fields['presenter_journalist'].required = False
        self.fields['timestamp'].required = False
        self.fields['context'].required = False


class MediaOutletForm(forms.ModelForm):
    """Form for adding new media outlets (admin only)"""

    class Meta:
        model = MediaOutlet
        fields = [
            'name',
            'media_type',
            'contact_email',
            'complaints_dept_email',
            'website',
            'regulator',
            'description',
            'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
