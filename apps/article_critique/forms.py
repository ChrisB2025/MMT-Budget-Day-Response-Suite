"""Forms for article critique submission."""
from django import forms
from .models import ArticleSubmission
from .extractors import validate_article_url, detect_publication


class ArticleURLSubmitForm(forms.ModelForm):
    """Form for submitting an article URL for critique."""

    class Meta:
        model = ArticleSubmission
        fields = ['original_url']
        widgets = {
            'original_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg',
                'placeholder': 'https://www.theguardian.com/...',
                'autocomplete': 'off',
                'autofocus': True,
            }),
        }
        labels = {
            'original_url': 'Article URL',
        }
        help_texts = {
            'original_url': 'Enter the full URL of the news article you want critiqued.',
        }

    def clean_original_url(self):
        url = self.cleaned_data.get('original_url', '').strip()

        if not url:
            raise forms.ValidationError('Please enter a URL.')

        # Validate URL format
        validation = validate_article_url(url)

        if not validation['valid']:
            raise forms.ValidationError(validation['error'])

        return url

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        if user:
            instance.user = user

        # Auto-detect publication
        instance.publication = detect_publication(instance.original_url)

        if commit:
            instance.save()

        return instance


class ArticleTextSubmitForm(forms.ModelForm):
    """Form for submitting article text directly (manual paste)."""

    class Meta:
        model = ArticleSubmission
        fields = ['title', 'author', 'publication', 'extracted_text', 'original_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Article title',
            }),
            'author': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Author name(s)',
            }),
            'publication': forms.Select(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            }),
            'extracted_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Paste the full article text here...',
                'rows': 12,
            }),
            'original_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'https://... (optional)',
            }),
        }
        labels = {
            'title': 'Article Title',
            'author': 'Author',
            'publication': 'Publication',
            'extracted_text': 'Article Text',
            'original_url': 'Original URL (optional)',
        }
        help_texts = {
            'extracted_text': 'Paste the full text of the article. This is useful for paywalled content.',
            'original_url': 'Include the URL if available, for reference.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_url'].required = False
        self.fields['title'].required = True
        self.fields['extracted_text'].required = True

    def clean_extracted_text(self):
        text = self.cleaned_data.get('extracted_text', '').strip()

        if not text:
            raise forms.ValidationError('Please paste the article text.')

        if len(text) < 100:
            raise forms.ValidationError('Article text is too short. Please paste the full article.')

        return text

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        if user:
            instance.user = user

        # Mark as manual extraction
        instance.extraction_method = 'manual'

        if commit:
            instance.save()

        return instance


class QuickResponseForm(forms.Form):
    """Form for regenerating quick responses with suggestions."""

    response_type = forms.ChoiceField(
        choices=[
            ('tweet', 'Tweet'),
            ('thread', 'Thread'),
            ('letter', 'Letter to Editor'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500',
        })
    )

    suggestions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Any specific points to emphasize or tone suggestions...',
            'rows': 3,
        }),
        help_text='Optional: Provide suggestions for improving the response.'
    )
