"""AI services for generating MMT critiques of news articles."""
import json
import logging
from typing import Dict, Any, List

from django.conf import settings
from anthropic import Anthropic

from .extractors import SITE_DOMAIN

logger = logging.getLogger(__name__)


# Main critique prompt for analyzing articles
ARTICLE_CRITIQUE_PROMPT = """You are an MMT economist analyzing economic journalism. Your task is to provide a rigorous, evidence-based critique of the article from a Modern Monetary Theory perspective.

ARTICLE INFORMATION:
Title: {title}
Author: {author}
Publication: {publication}
URL: {url}

ARTICLE TEXT:
{article_text}

Analyze this article and identify:
1. Factual errors - Claims that contradict economic reality
2. Framing issues - Misleading language (e.g., "taxpayer money" vs "public money", "national credit card", "government piggy bank")
3. MMT perspective - How MMT reframes the discussion
4. Missing context - Important information the article omits

Key MMT principles to apply:
- Currency-issuing governments (like the UK, US, Japan) aren't financially constrained like households
- Taxes don't fund federal government spending; they manage inflation and create demand for currency
- Real constraints are resources (labor, materials, capacity), not money
- Government deficit = non-government surplus (private sector savings)
- Unemployment is a policy choice, not an economic necessity

Return your analysis as JSON with these exact keys:
{{
    "summary": "2-3 sentence summary of the article's main economic claims and your overall assessment",
    "key_claims": ["list", "of", "main", "economic", "claims", "in", "the", "article"],
    "mmt_analysis": "Detailed MMT perspective (2-3 paragraphs) explaining how MMT reframes the issues discussed",
    "factual_errors": [
        {{
            "claim": "The specific claim made in the article",
            "problem": "What is factually wrong with this claim",
            "correction": "What the evidence actually shows"
        }}
    ],
    "framing_issues": [
        {{
            "issue": "Brief description of the framing issue",
            "problematic_framing": "The language or framing used in the article",
            "better_framing": "How this should be framed accurately"
        }}
    ],
    "missing_context": "Important context the article fails to provide (1-2 paragraphs)",
    "recommended_corrections": "Specific corrections the publication should make",
    "quick_rebuttal": "A single paragraph (150-200 words) that concisely rebuts the main misconceptions - suitable for social media or comment",
    "accuracy_rating": "one of: accurate, mostly_accurate, mixed, misleading, false",
    "confidence_score": 0.0 to 1.0 indicating confidence in your analysis,
    "citations": [
        {{"title": "Source title", "url": "https://..."}}
    ]
}}

Guidelines:
- Be rigorous and evidence-based, not rhetorical
- If the article is economically accurate, acknowledge this
- Focus on economic analysis, not political commentary
- Use accessible language that general readers can understand
- Cite specific MMT economists and research where relevant
- If there's insufficient economic content to analyze, explain this in the summary

Return ONLY valid JSON, no other text."""


# Quick response prompts
TWEET_PROMPT = """Based on this MMT critique of a news article, generate a tweet-length response.

ARTICLE: {title} by {author} ({publication})
SUMMARY: {summary}
KEY ISSUES: {key_issues}

Requirements:
- Maximum 280 characters (strict!)
- Be informative and respectful
- Focus on the key factual error or framing issue
- Don't use hashtags unless genuinely relevant
- Include a hook that makes people want to read the full critique

Return ONLY the tweet text, nothing else."""


THREAD_PROMPT = """Based on this MMT critique, generate a Twitter/X thread explaining the economic issues.

ARTICLE: {title} by {author} ({publication})
URL: {article_url}

CRITIQUE:
Summary: {summary}
Key Claims: {key_claims}
Factual Errors: {factual_errors}
Framing Issues: {framing_issues}
MMT Analysis: {mmt_analysis}

CRITIQUE URL: {critique_url}

Requirements:
- 4-6 posts, each under 280 characters
- First post should hook readers and reference the article
- Middle posts explain the key errors and MMT perspective
- Final post links to the full critique
- Number posts as 1/, 2/, etc.
- Be educational, not confrontational
- Use clear, accessible language

Return as JSON array of strings:
["Post 1/ text...", "Post 2/ text...", ...]

Return ONLY the JSON array, no other text."""


LETTER_PROMPT = """Based on this MMT critique, draft a formal letter to the editor correcting the article.

ARTICLE: {title}
AUTHOR: {author}
PUBLICATION: {publication}
DATE: {date}

CRITIQUE:
Summary: {summary}
Factual Errors: {factual_errors}
Recommended Corrections: {corrections}

Requirements:
- Professional, formal tone
- 200-300 words
- Open with "Dear Editor" or "To the Editor"
- Reference the specific article
- Focus on 1-2 key factual corrections
- Cite evidence where possible
- Close professionally
- Include placeholder for sender's name/credentials

Return ONLY the letter text."""


def generate_article_critique(
    article_text: str,
    title: str = '',
    author: str = '',
    publication: str = '',
    url: str = ''
) -> Dict[str, Any]:
    """
    Generate an MMT critique of a news article using Claude API.

    Args:
        article_text: The article text to analyze
        title: Article title
        author: Article author
        publication: Publication name
        url: Original article URL

    Returns:
        Dictionary containing the structured critique
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = ARTICLE_CRITIQUE_PROMPT.format(
        title=title or 'Not available',
        author=author or 'Unknown',
        publication=publication or 'Unknown',
        url=url or 'Not provided',
        article_text=article_text or 'Article text not available'
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
            'key_claims': data.get('key_claims', []),
            'mmt_analysis': data.get('mmt_analysis', ''),
            'factual_errors': data.get('factual_errors', []),
            'framing_issues': data.get('framing_issues', []),
            'missing_context': data.get('missing_context', ''),
            'recommended_corrections': data.get('recommended_corrections', ''),
            'quick_rebuttal': data.get('quick_rebuttal', ''),
            'accuracy_rating': data.get('accuracy_rating', 'mixed'),
            'confidence_score': float(data.get('confidence_score', 0.5)),
            'citations': data.get('citations', [])
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in critique generation: {e}")
        return {
            'summary': 'Error parsing AI response',
            'key_claims': [],
            'mmt_analysis': response_text if 'response_text' in locals() else 'Error generating analysis',
            'factual_errors': [],
            'framing_issues': [],
            'missing_context': '',
            'recommended_corrections': '',
            'quick_rebuttal': '',
            'accuracy_rating': 'mixed',
            'confidence_score': 0.0,
            'citations': []
        }
    except Exception as e:
        logger.error(f"Error calling Claude API for critique: {e}")
        raise Exception(f"Error generating critique: {str(e)}")


def generate_tweet_response(
    title: str,
    author: str,
    publication: str,
    summary: str,
    key_issues: str
) -> str:
    """Generate a tweet-length response."""
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = TWEET_PROMPT.format(
        title=title,
        author=author,
        publication=publication,
        summary=summary,
        key_issues=key_issues
    )

    try:
        message = client.messages.create(
            model='claude-3-5-haiku-20241022',  # Faster model for quick responses
            max_tokens=200,
            messages=[{'role': 'user', 'content': prompt}]
        )

        tweet = message.content[0].text.strip() if message.content else ''

        # Ensure within limit
        if len(tweet) > 280:
            tweet = tweet[:277] + '...'

        return tweet

    except Exception as e:
        logger.error(f"Error generating tweet: {e}")
        return f"Read our MMT analysis of this article:"[:280]


def generate_thread_response(
    title: str,
    author: str,
    publication: str,
    article_url: str,
    critique_url: str,
    summary: str,
    key_claims: List[str],
    factual_errors: List[Dict],
    framing_issues: List[Dict],
    mmt_analysis: str
) -> List[str]:
    """Generate a Twitter thread response."""
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Format errors and issues for prompt
    errors_text = '\n'.join([
        f"- {e['claim']}: {e['problem']}"
        for e in factual_errors[:3]
    ]) if factual_errors else 'None identified'

    issues_text = '\n'.join([
        f"- {i['issue']}: {i['problematic_framing']}"
        for i in framing_issues[:3]
    ]) if framing_issues else 'None identified'

    prompt = THREAD_PROMPT.format(
        title=title,
        author=author,
        publication=publication,
        article_url=article_url,
        critique_url=critique_url,
        summary=summary,
        key_claims=', '.join(key_claims[:5]),
        factual_errors=errors_text,
        framing_issues=issues_text,
        mmt_analysis=mmt_analysis[:500]
    )

    try:
        message = client.messages.create(
            model='claude-3-5-haiku-20241022',
            max_tokens=1500,
            messages=[{'role': 'user', 'content': prompt}]
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
            # Validate each post
            validated_thread = []
            for post in thread:
                if len(post) > 280:
                    post = post[:277] + '...'
                validated_thread.append(post)
            return validated_thread

        return [str(thread)]

    except json.JSONDecodeError:
        logger.error("JSON parse error in thread generation")
        return [
            f"1/ New article from {publication} contains economic misconceptions. Let's look at the facts...",
            f"2/ Read our full MMT analysis: {critique_url}"
        ]
    except Exception as e:
        logger.error(f"Error generating thread: {e}")
        return [f"Read our MMT analysis: {critique_url}"]


def generate_letter_response(
    title: str,
    author: str,
    publication: str,
    date: str,
    summary: str,
    factual_errors: List[Dict],
    corrections: str
) -> str:
    """Generate a letter to the editor."""
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Format errors for prompt
    errors_text = '\n'.join([
        f"- Claim: {e['claim']}\n  Problem: {e['problem']}\n  Correction: {e['correction']}"
        for e in factual_errors[:3]
    ]) if factual_errors else 'See summary'

    prompt = LETTER_PROMPT.format(
        title=title,
        author=author,
        publication=publication,
        date=date or 'Recent',
        summary=summary,
        factual_errors=errors_text,
        corrections=corrections
    )

    try:
        message = client.messages.create(
            model='claude-3-5-haiku-20241022',
            max_tokens=800,
            messages=[{'role': 'user', 'content': prompt}]
        )

        return message.content[0].text.strip() if message.content else ''

    except Exception as e:
        logger.error(f"Error generating letter: {e}")
        return "Dear Editor,\n\nI am writing to request a correction...\n\n[Error generating full letter]"


def process_article_submission(submission_id: int) -> Dict[str, Any]:
    """
    Process an article submission through the full pipeline.

    1. Extract article content (with paywall bypass if needed)
    2. Generate AI critique
    3. Generate quick responses (tweet, thread, letter)
    4. Save everything to database

    Args:
        submission_id: ArticleSubmission database ID

    Returns:
        Dictionary with status and any error message
    """
    from .models import ArticleSubmission, ArticleCritique, QuickResponse
    from .extractors import extract_article_with_cache, detect_publication

    try:
        submission = ArticleSubmission.objects.get(id=submission_id)
    except ArticleSubmission.DoesNotExist:
        return {'status': 'error', 'message': 'Submission not found'}

    # Update status
    submission.status = 'extracting'
    submission.save()

    try:
        # Step 1: Extract article content (if URL provided and no manual text)
        if submission.original_url and not submission.extracted_text:
            logger.info(f"Extracting content for submission {submission_id}: {submission.original_url}")

            extraction = extract_article_with_cache(submission.original_url)

            if extraction.get('success'):
                submission.extracted_text = extraction['text']
                submission.extraction_method = extraction['extraction_method']
                submission.archive_url = extraction.get('archive_url', '')
                submission.is_paywalled = extraction.get('is_paywalled', False)

                # Update metadata if not already set
                metadata = extraction.get('metadata', {})
                if not submission.title and metadata.get('title'):
                    submission.title = metadata['title'][:500]
                if not submission.author and metadata.get('author'):
                    submission.author = metadata['author'][:300]

                # Detect publication if not set
                if submission.publication == 'other':
                    submission.publication = detect_publication(submission.original_url)

            else:
                # Extraction failed
                errors = extraction.get('errors', [])
                error_msg = '; '.join([f"{e['method']}: {e['error']}" for e in errors])
                submission.status = 'failed'
                submission.error_message = f"Content extraction failed: {error_msg}"
                submission.is_paywalled = extraction.get('is_paywalled', True)
                submission.save()
                return {'status': 'error', 'message': submission.error_message}

        # Check we have content to analyze
        if not submission.extracted_text:
            submission.status = 'failed'
            submission.error_message = 'No article content available for analysis'
            submission.save()
            return {'status': 'error', 'message': submission.error_message}

        submission.status = 'analyzing'
        submission.save()

        # Step 2: Generate AI critique
        logger.info(f"Generating critique for submission {submission_id}")

        if not settings.ANTHROPIC_API_KEY:
            raise Exception("ANTHROPIC_API_KEY not configured")

        critique_data = generate_article_critique(
            article_text=submission.extracted_text,
            title=submission.title,
            author=submission.author,
            publication=submission.get_publication_display_name(),
            url=submission.original_url
        )

        # Create critique record
        critique = ArticleCritique.objects.create(
            article=submission,
            summary=critique_data['summary'],
            key_claims=critique_data['key_claims'],
            mmt_analysis=critique_data['mmt_analysis'],
            factual_errors=critique_data['factual_errors'],
            framing_issues=critique_data['framing_issues'],
            missing_context=critique_data['missing_context'],
            recommended_corrections=critique_data['recommended_corrections'],
            quick_rebuttal=critique_data['quick_rebuttal'],
            accuracy_rating=critique_data['accuracy_rating'],
            confidence_score=critique_data['confidence_score'],
            citations=critique_data['citations']
        )

        # Step 3: Generate quick responses
        logger.info(f"Generating quick responses for submission {submission_id}")
        submission.status = 'generating'
        submission.save()

        critique_url = f"https://{SITE_DOMAIN}/articles/share/{submission.share_id}/"

        # Generate tweet
        try:
            key_issues = critique_data['quick_rebuttal'] or critique_data['summary']
            tweet = generate_tweet_response(
                title=submission.title,
                author=submission.author,
                publication=submission.get_publication_display_name(),
                summary=critique_data['summary'],
                key_issues=key_issues
            )
            QuickResponse.objects.update_or_create(
                article=submission,
                response_type='tweet',
                defaults={
                    'content': tweet,
                    'char_count': len(tweet),
                    'thread_parts': []
                }
            )
        except Exception as e:
            logger.error(f"Error generating tweet: {e}")

        # Generate thread
        try:
            thread_parts = generate_thread_response(
                title=submission.title,
                author=submission.author,
                publication=submission.get_publication_display_name(),
                article_url=submission.original_url,
                critique_url=critique_url,
                summary=critique_data['summary'],
                key_claims=critique_data['key_claims'],
                factual_errors=critique_data['factual_errors'],
                framing_issues=critique_data['framing_issues'],
                mmt_analysis=critique_data['mmt_analysis']
            )
            QuickResponse.objects.update_or_create(
                article=submission,
                response_type='thread',
                defaults={
                    'content': '\n\n---\n\n'.join(thread_parts),
                    'char_count': sum(len(p) for p in thread_parts),
                    'thread_parts': thread_parts
                }
            )
        except Exception as e:
            logger.error(f"Error generating thread: {e}")

        # Generate letter to editor
        try:
            letter = generate_letter_response(
                title=submission.title,
                author=submission.author,
                publication=submission.get_publication_display_name(),
                date=submission.publication_date.strftime('%d %B %Y') if submission.publication_date else '',
                summary=critique_data['summary'],
                factual_errors=critique_data['factual_errors'],
                corrections=critique_data['recommended_corrections']
            )
            QuickResponse.objects.update_or_create(
                article=submission,
                response_type='letter',
                defaults={
                    'content': letter,
                    'char_count': len(letter),
                    'thread_parts': []
                }
            )
        except Exception as e:
            logger.error(f"Error generating letter: {e}")

        # Update status to completed
        submission.status = 'completed'
        submission.save()

        logger.info(f"Submission {submission_id} processed successfully")
        return {'status': 'success', 'critique_id': critique.id}

    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {str(e)}")
        submission.status = 'failed'
        submission.error_message = str(e)
        submission.save()
        return {'status': 'error', 'message': str(e)}
