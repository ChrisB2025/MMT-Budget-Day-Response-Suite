"""Forms for social media critique submission"""
from django import forms
from .models import SocialMediaCritique
from .fetchers import validate_url, detect_platform


class SocialCritiqueSubmitForm(forms.ModelForm):
    """Form for submitting a social media URL for critique"""

    class Meta:
        model = SocialMediaCritique
        fields = ['url']
        widgets = {
            'url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg',
                'placeholder': 'Paste a YouTube, Twitter/X, or other social media URL...',
                'autocomplete': 'off',
                'autofocus': True,
            }),
        }
        labels = {
            'url': 'Social Media URL',
        }
        help_texts = {
            'url': 'Enter the full URL of a social media post, video, or article you want critiqued from an MMT perspective.',
        }

    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()

        if not url:
            raise forms.ValidationError('Please enter a URL.')

        # Validate URL format and accessibility
        validation = validate_url(url)

        if not validation['valid']:
            raise forms.ValidationError(validation['error'])

        return url

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        if user:
            instance.user = user

        # Auto-detect platform
        instance.platform = detect_platform(instance.url)

        if commit:
            instance.save()

        return instance


class URLPreviewForm(forms.Form):
    """Simple form for AJAX URL preview"""
    url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-2 rounded border border-gray-300 focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter URL to preview...',
        })
    )

    def clean_url(self):
        url = self.cleaned_data.get('url', '').strip()
        validation = validate_url(url)

        if not validation['valid']:
            raise forms.ValidationError(validation['error'])

        return url
