"""AI services for generating MMT critiques of social media content"""
import json
import logging
from typing import Dict, Any, List, Optional

from django.conf import settings
from anthropic import Anthropic

from .fetchers import PLATFORM_CHAR_LIMITS

logger = logging.getLogger(__name__)


# Main critique prompt for analyzing social media content
CRITIQUE_PROMPT = """You are an expert economist specializing in Modern Monetary Theory (MMT). You're analyzing social media content to identify economic claims and provide an evidence-based MMT perspective.

SOURCE INFORMATION:
Platform: {platform}
Title: {title}
Author: {author}
Content: {content}
URL: {url}

Analyze this content from an MMT perspective and provide a structured critique. Focus on:
1. Identifying any economic claims or assumptions (explicit or implicit)
2. Evaluating the accuracy of these claims
3. Providing the MMT perspective on these economic issues
4. Citing evidence and sources where relevant

Return your analysis as JSON with these exact keys:
{{
    "summary": "2-3 sentence summary of what this content is about and its main economic claims",
    "claims_identified": ["list", "of", "specific", "economic", "claims", "found"],
    "mmt_analysis": "Detailed MMT perspective analysis (2-3 paragraphs explaining how MMT reframes these issues)",
    "key_misconceptions": "Key economic misconceptions or misleading framings identified (be specific about what's wrong and why)",
    "reality_check": "What the evidence actually shows - cite specific data, studies, or facts",
    "accuracy_rating": "one of: accurate, mostly_accurate, mixed, misleading, false",
    "confidence_score": 0.0 to 1.0 indicating confidence in analysis,
    "recommended_reading": [
        {{"title": "Resource title", "url": "https://...", "description": "Why this is relevant"}}
    ],
    "citations": [
        {{"title": "Citation title", "url": "https://..."}}
    ]
}}

Guidelines:
- Be fair and evidence-based, not rhetorical or dismissive
- If the content is accurate, say so - MMT economists can agree with mainstream views when they're correct
- Focus on the economics, not political commentary
- Use accessible language that general audiences can understand
- If there's not enough economic content to analyze, say so clearly in the summary

Return ONLY valid JSON, no other text."""


# Reply generation prompts
SHORT_REPLY_PROMPT = """Based on this MMT analysis of social media content, generate a short reply suitable for posting on {platform}.

ANALYSIS SUMMARY:
{summary}

KEY POINTS:
{key_points}

CRITIQUE URL: {critique_url}

Requirements:
- Maximum {char_limit} characters (this is strict!)
- Be respectful but factual
- Include the key insight or correction
- End with a link to the full analysis
- Don't use hashtags unless they're genuinely relevant
- Avoid being preachy or condescending

Return ONLY the reply text, nothing else. Count characters carefully."""


THREAD_REPLY_PROMPT = """Based on this MMT analysis, generate a thread suitable for {platform}.

FULL ANALYSIS:
Summary: {summary}
Claims: {claims}
MMT Analysis: {mmt_analysis}
Key Misconceptions: {misconceptions}
Reality Check: {reality}

CRITIQUE URL: {critique_url}

Requirements:
- Each post must be under {char_limit} characters
- Create 4-6 posts that flow logically
- First post should hook the reader and reference the original content
- Middle posts cover the main analysis
- Final post includes the link to full analysis
- Number each post (1/n format)
- Be educational, not confrontational

Return as JSON array of strings, each string being one post in the thread:
["Post 1/n text here...", "Post 2/n text here...", ...]

Return ONLY the JSON array, no other text."""


SUMMARY_CARD_PROMPT = """Create a brief summary card text for sharing this MMT critique.

ANALYSIS:
Title of original: {title}
Author: {author}
Platform: {platform}
Summary: {summary}
Accuracy Rating: {rating}

CRITIQUE URL: {critique_url}

Requirements:
- Maximum 200 characters
- Should work as a preview/teaser
- Include the accuracy rating clearly
- Be objective and informative

Return ONLY the summary text, nothing else."""


def generate_critique_with_claude(
    content: str,
    platform: str,
    title: str = '',
    author: str = '',
    url: str = ''
) -> Dict[str, Any]:
    """
    Generate an MMT critique of social media content using Claude API.

    Args:
        content: The text content to analyze
        platform: Social media platform name
        title: Title of the content (optional)
        author: Author name (optional)
        url: Original URL (optional)

    Returns:
        Dictionary containing:
            - summary: Brief summary
            - claims_identified: List of claims found
            - mmt_analysis: MMT perspective
            - key_misconceptions: Identified misconceptions
            - reality_check: Evidence-based reality
            - accuracy_rating: Rating string
            - confidence_score: Float 0-1
            - recommended_reading: List of resources
            - citations: List of citations
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = CRITIQUE_PROMPT.format(
        platform=platform,
        title=title or 'Not available',
        author=author or 'Unknown',
        content=content or 'Content could not be extracted',
        url=url or 'Not provided'
    )

    try:
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

        response_text = message.content[0].text if message.content else ''

        # Clean markdown code blocks if present
        cleaned = response_text.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Parse JSON
        data = json.loads(cleaned)

        return {
            'summary': data.get('summary', ''),
            'claims_identified': data.get('claims_identified', []),
            'mmt_analysis': data.get('mmt_analysis', ''),
            'key_misconceptions': data.get('key_misconceptions', ''),
            'reality_check': data.get('reality_check', ''),
            'accuracy_rating': data.get('accuracy_rating', 'mixed'),
            'confidence_score': float(data.get('confidence_score', 0.5)),
            'recommended_reading': data.get('recommended_reading', []),
            'citations': data.get('citations', [])
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in critique generation: {e}")
        return {
            'summary': 'Error parsing AI response',
            'claims_identified': [],
            'mmt_analysis': response_text if 'response_text' in locals() else 'Error generating analysis',
            'key_misconceptions': '',
            'reality_check': '',
            'accuracy_rating': 'mixed',
            'confidence_score': 0.0,
            'recommended_reading': [],
            'citations': []
        }
    except Exception as e:
        logger.error(f"Error calling Claude API for critique: {e}")
        raise Exception(f"Error generating critique: {str(e)}")


def generate_short_reply(
    summary: str,
    key_points: str,
    platform: str,
    critique_url: str
) -> str:
    """
    Generate a short reply suitable for the target platform.

    Args:
        summary: Summary of the critique
        key_points: Key points to highlight
        platform: Target platform
        critique_url: URL to the full critique

    Returns:
        String containing the reply text
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    char_limit = PLATFORM_CHAR_LIMITS.get(platform, 280)

    prompt = SHORT_REPLY_PROMPT.format(
        platform=platform,
        summary=summary,
        key_points=key_points,
        critique_url=critique_url,
        char_limit=char_limit
    )

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=500,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        reply = message.content[0].text.strip() if message.content else ''

        # Ensure within limit (truncate if necessary)
        if len(reply) > char_limit:
            # Try to truncate at word boundary
            reply = reply[:char_limit-3].rsplit(' ', 1)[0] + '...'

        return reply

    except Exception as e:
        logger.error(f"Error generating short reply: {e}")
        # Fallback reply
        fallback = f"Check out this MMT analysis: {critique_url}"
        return fallback[:char_limit]


def generate_thread_reply(
    analysis: Dict[str, Any],
    platform: str,
    critique_url: str
) -> List[str]:
    """
    Generate a thread-style reply for the target platform.

    Args:
        analysis: Full critique analysis dictionary
        platform: Target platform
        critique_url: URL to the full critique

    Returns:
        List of strings, each being one post in the thread
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    char_limit = PLATFORM_CHAR_LIMITS.get(platform, 280)

    # Format claims as bullet points
    claims = '\n'.join(f"- {c}" for c in analysis.get('claims_identified', []))

    prompt = THREAD_REPLY_PROMPT.format(
        platform=platform,
        summary=analysis.get('summary', ''),
        claims=claims or 'No specific claims identified',
        mmt_analysis=analysis.get('mmt_analysis', ''),
        misconceptions=analysis.get('key_misconceptions', ''),
        reality=analysis.get('reality_check', ''),
        critique_url=critique_url,
        char_limit=char_limit
    )

    try:
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

        response_text = message.content[0].text.strip() if message.content else ''

        # Clean markdown code blocks
        cleaned = response_text
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Parse JSON array
        thread = json.loads(cleaned)

        if isinstance(thread, list):
            # Validate each post is within limit
            validated_thread = []
            for i, post in enumerate(thread):
                if len(post) > char_limit:
                    post = post[:char_limit-3].rsplit(' ', 1)[0] + '...'
                validated_thread.append(post)
            return validated_thread

        return [str(thread)]

    except json.JSONDecodeError:
        logger.error(f"JSON parse error in thread generation")
        # Return simple fallback thread
        return [
            f"1/2 Interesting content - here's an MMT perspective analysis...",
            f"2/2 Read the full analysis: {critique_url}"
        ]
    except Exception as e:
        logger.error(f"Error generating thread: {e}")
        return [f"Check out this MMT analysis: {critique_url}"]


def generate_summary_card(
    title: str,
    author: str,
    platform: str,
    summary: str,
    rating: str,
    critique_url: str
) -> str:
    """
    Generate a brief summary card text for sharing.

    Returns:
        String containing summary card text (max 200 chars)
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = SUMMARY_CARD_PROMPT.format(
        title=title,
        author=author,
        platform=platform,
        summary=summary,
        rating=rating,
        critique_url=critique_url
    )

    try:
        message = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=100,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )

        card_text = message.content[0].text.strip() if message.content else ''

        # Ensure within 200 chars
        if len(card_text) > 200:
            card_text = card_text[:197] + '...'

        return card_text

    except Exception as e:
        logger.error(f"Error generating summary card: {e}")
        rating_display = rating.replace('_', ' ').title()
        return f"MMT Analysis: {rating_display}"[:200]


def process_social_critique(critique_id: int) -> Dict[str, Any]:
    """
    Process a social media critique request.

    This is the main processing function that:
    1. Fetches content from the URL
    2. Generates AI critique
    3. Creates shareable replies
    4. Saves everything to database

    Args:
        critique_id: SocialMediaCritique database ID

    Returns:
        Dictionary with status and any error message
    """
    from .models import SocialMediaCritique, CritiqueResponse, ShareableReply
    from .fetchers import fetch_with_cache

    try:
        critique = SocialMediaCritique.objects.get(id=critique_id)
    except SocialMediaCritique.DoesNotExist:
        return {'status': 'error', 'message': 'Critique not found'}

    # Update status
    critique.status = 'fetching'
    critique.save()

    try:
        # Step 1: Fetch content
        logger.info(f"Fetching content for critique {critique_id}: {critique.url}")
        content = fetch_with_cache(critique.url)

        if content.get('error'):
            critique.status = 'failed'
            critique.error_message = content['error']
            critique.save()
            return {'status': 'error', 'message': content['error']}

        # Update critique with fetched content
        critique.platform = content.get('platform', critique.platform)
        critique.source_title = content.get('title', '')[:500]
        critique.source_author = content.get('author', '')[:200]
        critique.source_text = content.get('text', '')
        critique.source_description = content.get('description', '')
        critique.source_thumbnail_url = content.get('thumbnail_url', '')[:2048]
        critique.source_publish_date = content.get('publish_date')
        critique.status = 'processing'
        critique.save()

        # Step 2: Generate AI critique
        logger.info(f"Generating AI critique for {critique_id}")

        if not settings.ANTHROPIC_API_KEY:
            raise Exception("ANTHROPIC_API_KEY not configured")

        # Combine text and description for analysis
        analysis_content = critique.source_text or critique.source_description
        if not analysis_content:
            analysis_content = critique.source_title or 'Content could not be extracted from URL'

        critique_data = generate_critique_with_claude(
            content=analysis_content,
            platform=critique.platform,
            title=critique.source_title,
            author=critique.source_author,
            url=critique.url
        )

        # Create response record
        response = CritiqueResponse.objects.create(
            critique=critique,
            summary=critique_data['summary'],
            claims_identified=critique_data['claims_identified'],
            mmt_analysis=critique_data['mmt_analysis'],
            key_misconceptions=critique_data['key_misconceptions'],
            reality_check=critique_data['reality_check'],
            accuracy_rating=critique_data['accuracy_rating'],
            confidence_score=critique_data['confidence_score'],
            recommended_reading=critique_data['recommended_reading'],
            citations=critique_data['citations']
        )

        # Step 3: Generate shareable replies
        logger.info(f"Generating shareable replies for {critique_id}")

        # Build critique URL (will need domain from request in production)
        critique_url = f"/critique/{critique.share_id}/"

        # Generate for original platform
        _generate_and_save_replies(critique, response, critique.platform, critique_url)

        # Also generate for Twitter if different platform
        if critique.platform != 'twitter':
            _generate_and_save_replies(critique, response, 'twitter', critique_url)

        # Update status to completed
        critique.status = 'completed'
        critique.save()

        logger.info(f"Critique {critique_id} processed successfully")
        return {'status': 'success', 'response_id': response.id}

    except Exception as e:
        logger.error(f"Error processing critique {critique_id}: {str(e)}")
        critique.status = 'failed'
        critique.error_message = str(e)
        critique.save()
        return {'status': 'error', 'message': str(e)}


def _generate_and_save_replies(critique, response, platform: str, critique_url: str):
    """Helper to generate and save shareable replies for a platform"""
    from .models import ShareableReply

    # Prepare key points for short reply
    key_points = response.key_misconceptions or response.summary

    # Generate short reply
    try:
        short_reply = generate_short_reply(
            summary=response.summary,
            key_points=key_points,
            platform=platform,
            critique_url=critique_url
        )

        ShareableReply.objects.update_or_create(
            critique=critique,
            reply_type='short',
            platform_target=platform,
            defaults={
                'content': short_reply,
                'char_count': len(short_reply),
                'thread_parts': []
            }
        )
    except Exception as e:
        logger.error(f"Error generating short reply for {platform}: {e}")

    # Generate thread reply
    try:
        thread_parts = generate_thread_reply(
            analysis={
                'summary': response.summary,
                'claims_identified': response.claims_identified,
                'mmt_analysis': response.mmt_analysis,
                'key_misconceptions': response.key_misconceptions,
                'reality_check': response.reality_check
            },
            platform=platform,
            critique_url=critique_url
        )

        # Combine for display
        thread_content = '\n\n---\n\n'.join(thread_parts)

        ShareableReply.objects.update_or_create(
            critique=critique,
            reply_type='thread',
            platform_target=platform,
            defaults={
                'content': thread_content,
                'char_count': sum(len(p) for p in thread_parts),
                'thread_parts': thread_parts
            }
        )
    except Exception as e:
        logger.error(f"Error generating thread for {platform}: {e}")

    # Generate summary card
    try:
        summary_card = generate_summary_card(
            title=critique.source_title,
            author=critique.source_author,
            platform=critique.platform,
            summary=response.summary,
            rating=response.accuracy_rating,
            critique_url=critique_url
        )

        ShareableReply.objects.update_or_create(
            critique=critique,
            reply_type='summary',
            platform_target=platform,
            defaults={
                'content': summary_card,
                'char_count': len(summary_card),
                'thread_parts': []
            }
        )
    except Exception as e:
        logger.error(f"Error generating summary card for {platform}: {e}")
