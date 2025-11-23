"""Claude API service for generating complaint letters with variation"""
import json
import logging
from django.conf import settings
from django.utils import timezone
from anthropic import Anthropic

logger = logging.getLogger(__name__)


# Variation strategy prompts
VARIATION_STRATEGIES = {
    'correction': {
        'emphasis': 'Request a public correction and clarification of the misinformation',
        'action_requested': 'publish a correction, update online content, and clarify in future coverage'
    },
    'training': {
        'emphasis': 'Request staff training on economic literacy and MMT principles',
        'action_requested': 'provide training to journalists and presenters on government finance fundamentals'
    },
    'policy': {
        'emphasis': 'Request a review of editorial policies regarding economic reporting',
        'action_requested': 'review editorial guidelines to ensure accurate economic reporting'
    },
    'investigation': {
        'emphasis': 'Request an internal investigation into the accuracy of the reporting',
        'action_requested': 'investigate how this misinformation was broadcast and implement quality controls'
    },
    'accountability': {
        'emphasis': 'Emphasize the outlet\'s accountability to the public and regulatory standards',
        'action_requested': 'acknowledge the error and commit to higher standards of economic reporting'
    }
}


# Tone variations
TONE_PROFILES = {
    'professional': {
        'style': 'formal, measured, business-like',
        'greeting': 'Dear Sir/Madam',
        'closing': 'Yours faithfully'
    },
    'academic': {
        'style': 'scholarly, evidence-focused, pedagogical',
        'greeting': 'To the Editorial Team',
        'closing': 'Respectfully submitted'
    },
    'passionate': {
        'style': 'assertive, concerned citizen, direct',
        'greeting': 'To whom it may concern',
        'closing': 'Sincerely concerned'
    }
}


def get_variation_strategy(complaint_number):
    """
    Determine which variation strategy to use based on complaint number.

    Args:
        complaint_number: Which complaint this is for the incident (1, 2, 3...)

    Returns:
        str: strategy key
    """
    strategies = list(VARIATION_STRATEGIES.keys())
    # Cycle through strategies
    strategy_index = (complaint_number - 1) % len(strategies)
    return strategies[strategy_index]


# Letter generation prompt
LETTER_PROMPT = """You are helping a UK citizen write a complaint letter to a media outlet about economic misinformation.

MEDIA OUTLET: {outlet_name}
OUTLET TYPE: {outlet_type}
REGULATOR: {regulator}

INCIDENT DETAILS:
- Date: {incident_date}
- Programme/Article: {programme_name}
- Presenter/Journalist: {presenter_journalist}
- Timestamp: {timestamp}

THE MISINFORMATION:
{claim_description}

ADDITIONAL CONTEXT:
{context}

SEVERITY: {severity}/5

LETTER REQUIREMENTS:
1. TONE: {tone_style}
2. GREETING: {greeting}
3. VARIATION STRATEGY: {variation_emphasis}
4. ACTION REQUESTED: {action_requested}
5. CLOSING: {closing}

COMPLAINT NUMBER: This is complaint #{complaint_number} about this incident, so make the letter SUBSTANTIALLY DIFFERENT from typical complaint letters. Vary:
- Opening paragraph structure
- Order of arguments
- Specific examples emphasized
- Length and detail of MMT explanation

MMT PERSPECTIVE REQUIRED:
Include 1-2 paragraphs explaining the MMT perspective on this issue. Choose from relevant points:
- Government creates money through spending, not constrained by "taxpayer money"
- Government deficits = private sector surpluses
- Currency-issuing governments cannot "run out of money"
- Real constraints are inflation and real resources, not financial
- National debt is actually private sector savings
- Household budget analogy is fundamentally misleading

Generate a complete, professional complaint letter in this structure:

1. Subject line (formal, specific)
2. Greeting
3. Opening paragraph (state purpose, identify incident)
4. The problem (explain the misinformation, 2-3 paragraphs)
5. The evidence (why this is incorrect, with MMT perspective)
6. Impact concern (why this matters to the public)
7. Action requested (specific, based on variation strategy)
8. Closing paragraph
9. Sign-off

Return as JSON with these keys:
- subject: Email subject line
- body: Complete letter body (include greeting, all paragraphs, closing)
- mmt_points: Array of MMT points addressed in the letter
- variation_used: Which variation strategy was primarily used

Return ONLY valid JSON, no other text."""


def generate_complaint_letter(complaint):
    """
    Generate a complaint letter using Claude API with variation.

    Args:
        complaint: Complaint model instance

    Returns:
        dict with letter data: subject, body, mmt_points, variation_used
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Determine variation strategy
    strategy_key = get_variation_strategy(complaint.complaint_number_for_incident)
    strategy = VARIATION_STRATEGIES[strategy_key]

    # Get tone profile
    tone = TONE_PROFILES.get(complaint.preferred_tone, TONE_PROFILES['professional'])

    # Build prompt
    prompt = LETTER_PROMPT.format(
        outlet_name=complaint.outlet.name,
        outlet_type=complaint.outlet.get_media_type_display(),
        regulator=complaint.outlet.regulator or 'relevant regulatory body',
        incident_date=complaint.incident_date.strftime('%d %B %Y'),
        programme_name=complaint.programme_name,
        presenter_journalist=complaint.presenter_journalist or 'the presenter/journalist',
        timestamp=complaint.timestamp or 'during the programme',
        claim_description=complaint.claim_description,
        context=complaint.context or 'No additional context provided',
        severity=complaint.severity,
        tone_style=tone['style'],
        greeting=tone['greeting'],
        variation_emphasis=strategy['emphasis'],
        action_requested=strategy['action_requested'],
        closing=tone['closing'],
        complaint_number=complaint.complaint_number_for_incident
    )

    try:
        logger.info(f"Generating letter for complaint {complaint.id} (variation: {strategy_key})")

        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        # Extract text from response
        response_text = message.content[0].text if message.content else ''

        # Clean up response - remove markdown code blocks if present
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        # Parse JSON response
        letter_data = json.loads(cleaned_text)

        return {
            'subject': letter_data.get('subject', f'Complaint regarding {complaint.programme_name}'),
            'body': letter_data.get('body', ''),
            'mmt_points': letter_data.get('mmt_points', []),
            'variation_used': strategy_key
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for complaint {complaint.id}: {e}")
        # Fallback: generate a basic letter structure
        return generate_fallback_letter(complaint, strategy_key, tone)

    except Exception as e:
        logger.error(f"Error generating letter for complaint {complaint.id}: {e}")
        raise Exception(f"Error calling Claude API: {str(e)}")


def generate_fallback_letter(complaint, strategy_key, tone):
    """
    Generate a basic fallback letter if AI generation fails.

    Args:
        complaint: Complaint instance
        strategy_key: Variation strategy
        tone: Tone profile

    Returns:
        dict with basic letter structure
    """
    strategy = VARIATION_STRATEGIES[strategy_key]

    body = f"""{tone['greeting']},

I am writing to formally complain about misinformation broadcast on {complaint.programme_name} on {complaint.incident_date.strftime('%d %B %Y')}.

The issue concerns: {complaint.claim_description}

This type of economic misinformation is harmful to public understanding. From a Modern Monetary Theory perspective, it's important to recognize that currency-issuing governments like the UK are not financially constrained in the way households are.

I request that you {strategy['action_requested']}.

{tone['closing']},
A Concerned Viewer"""

    return {
        'subject': f'Complaint regarding {complaint.programme_name} - {complaint.incident_date.strftime("%d %B %Y")}',
        'body': body,
        'mmt_points': ['government_budget_not_like_household'],
        'variation_used': strategy_key
    }


def process_complaint_letter(complaint_id):
    """
    Generate a complaint letter for a pending complaint.

    Args:
        complaint_id: Complaint ID

    Returns:
        dict with status and letter_id or error message
    """
    from .models import Complaint, ComplaintLetter

    try:
        complaint = Complaint.objects.get(id=complaint_id)
    except Complaint.DoesNotExist:
        logger.error(f"Complaint {complaint_id} not found")
        return {'status': 'error', 'message': 'Complaint not found'}

    # Update status
    complaint.status = 'pending'
    complaint.save()

    try:
        logger.info(f"Processing complaint letter for complaint {complaint_id}")

        # Check if API key is configured
        if not settings.ANTHROPIC_API_KEY:
            raise Exception("ANTHROPIC_API_KEY not configured in settings")

        # Generate letter
        letter_data = generate_complaint_letter(complaint)

        # Create ComplaintLetter
        letter = ComplaintLetter.objects.create(
            complaint=complaint,
            subject=letter_data['subject'],
            body=letter_data['body'],
            variation_strategy=letter_data['variation_used'],
            tone_used=complaint.preferred_tone,
            mmt_points_included=letter_data['mmt_points']
        )

        # Update complaint status
        complaint.status = 'generated'
        complaint.save()

        logger.info(f"Successfully generated letter {letter.id} for complaint {complaint_id}")

        return {
            'status': 'success',
            'letter_id': letter.id
        }

    except Exception as e:
        logger.error(f"Error processing complaint {complaint_id}: {e}")
        complaint.status = 'draft'
        complaint.save()

        return {
            'status': 'error',
            'message': str(e)
        }


def send_complaint_email(letter_id):
    """
    Send a complaint letter via email.

    Args:
        letter_id: ComplaintLetter ID

    Returns:
        dict with status
    """
    from django.core.mail import send_mail
    from .models import ComplaintLetter

    try:
        letter = ComplaintLetter.objects.select_related('complaint', 'complaint__outlet').get(id=letter_id)
    except ComplaintLetter.DoesNotExist:
        return {'status': 'error', 'message': 'Letter not found'}

    complaint = letter.complaint
    outlet = complaint.outlet

    # Determine recipient email
    recipient_email = outlet.complaints_dept_email or outlet.contact_email

    try:
        # Send email
        send_mail(
            subject=letter.subject,
            message=letter.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        # Mark as sent
        letter.mark_as_sent(recipient_email)

        # Update user stats
        from .models import ComplaintStats
        stats, created = ComplaintStats.objects.get_or_create(user=complaint.user)
        stats.update_stats()

        logger.info(f"Successfully sent letter {letter_id} to {recipient_email}")

        return {
            'status': 'success',
            'sent_to': recipient_email
        }

    except Exception as e:
        logger.error(f"Error sending email for letter {letter_id}: {e}")
        return {
            'status': 'error',
            'message': f"Failed to send email: {str(e)}"
        }


def get_or_create_complaint_stats(user):
    """Get or create complaint statistics for a user"""
    from .models import ComplaintStats

    stats, created = ComplaintStats.objects.get_or_create(user=user)
    if not created:
        stats.update_stats()
    return stats


def research_media_outlet(outlet_name, media_type, website=''):
    """
    Use Claude AI to research complaints contact information for a media outlet.

    Args:
        outlet_name: Name of the media outlet
        media_type: Type of media (tv, radio, print, online)
        website: Optional website URL

    Returns:
        dict with: contact_email, complaints_email, regulator, notes
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""You are researching contact information for a UK media outlet.

OUTLET NAME: {outlet_name}
MEDIA TYPE: {media_type}
WEBSITE: {website or 'Not provided'}

Please research and provide the following information:

1. CONTACT EMAIL: General contact email address
2. COMPLAINTS EMAIL: Specific complaints department email (if different from general)
3. REGULATOR: Which UK regulator oversees this outlet (e.g., Ofcom for broadcast, IPSO for print)
4. NOTES: Any additional information about complaint procedures

Based on your knowledge of UK media outlets and typical structures:
- For BBC outlets: complaints@bbc.co.uk
- For Ofcom-regulated broadcasters: Look for viewer services emails
- For print media: Look for editorial complaints or readers' editor emails
- For online: Check if they follow IPSO or another regulator

Return as JSON with these exact keys: contact_email, complaints_email, regulator, notes

Return ONLY valid JSON, no other text."""

    try:
        logger.info(f"Researching outlet: {outlet_name}")

        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=2000,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        # Extract text from response
        response_text = message.content[0].text if message.content else ''

        # Clean up response
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        elif cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]

        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]

        cleaned_text = cleaned_text.strip()

        # Parse JSON response
        research_data = json.loads(cleaned_text)

        return {
            'contact_email': research_data.get('contact_email', ''),
            'complaints_email': research_data.get('complaints_email', ''),
            'regulator': research_data.get('regulator', ''),
            'notes': research_data.get('notes', '')
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error for outlet research {outlet_name}: {e}")
        # Return basic fallback
        return {
            'contact_email': '',
            'complaints_email': '',
            'regulator': 'Ofcom' if media_type in ['tv', 'radio'] else 'IPSO',
            'notes': 'AI research failed - please verify contact details manually'
        }

    except Exception as e:
        logger.error(f"Error researching outlet {outlet_name}: {e}")
        return {
            'contact_email': '',
            'complaints_email': '',
            'regulator': '',
            'notes': f'Research error: {str(e)}'
        }
