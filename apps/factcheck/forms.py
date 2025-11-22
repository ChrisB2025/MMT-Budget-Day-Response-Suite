"""Fact-check forms"""
from django import forms
from .models import FactCheckRequest


class FactCheckSubmitForm(forms.ModelForm):
    """Form for submitting fact-check requests"""

    class Meta:
        model = FactCheckRequest
        fields = ['claim_text', 'context', 'timestamp_in_speech', 'severity']
        widgets = {
            'claim_text': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Enter the claim you want fact-checked...'
            }),
            'context': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 3,
                'placeholder': 'Additional context (optional)'
            }),
            'timestamp_in_speech': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'e.g., 12:45:30'
            }),
            'severity': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'
            })
        }
        labels = {
            'claim_text': 'Claim to Fact-Check',
            'context': 'Additional Context',
            'timestamp_in_speech': 'Timestamp in Speech',
            'severity': 'Severity Rating (1-10)'
        }
