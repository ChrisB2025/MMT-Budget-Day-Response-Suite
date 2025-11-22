"""Claude API service for rebuttal generation"""
import json
from django.conf import settings
from anthropic import Anthropic


# Prompt template for rebuttal generation
REBUTTAL_PROMPT = """You are an expert MMT economist creating a comprehensive rebuttal to the UK Budget speech.

INPUTS:
- Budget speech transcript: {transcript}
- Top community-flagged claims: {priority_claims}

Generate a comprehensive rebuttal document with these sections:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - What the Chancellor said
   - What MMT reveals about the reality
   - Key takeaways

2. KEY MYTHS DEBUNKED (Top 5-10)
   For each myth:
   - The claim
   - Why it's wrong
   - What's actually true
   - Evidence

3. FISCAL ANALYSIS
   - Debt/deficit rhetoric deconstruction
   - Tax vs spending framing critique
   - Resource vs financial constraint analysis

4. WHAT THEY DIDN'T SAY
   - Important omissions
   - Questions they avoided

5. ACTION POINTS
   - For activists: 3-5 talking points
   - For MPs: 3 suggested parliamentary questions
   - For media: Alternative framing suggestions

Use citations throughout. Be rigorous but accessible. Target audience: educated general public, activists, journalists.

Return as JSON with an array of section objects containing: title, content, order.

Important: Return ONLY valid JSON, no other text."""


def generate_rebuttal_with_claude(transcript='', priority_claims=None):
    """
    Generate a comprehensive rebuttal using Claude API.

    Args:
        transcript: Full budget speech transcript (optional)
        priority_claims: List of priority claim texts (optional)

    Returns:
        dict with rebuttal sections
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    # Format priority claims
    claims_text = ''
    if priority_claims:
        claims_text = '\n'.join([f"- {claim}" for claim in priority_claims])

    prompt = REBUTTAL_PROMPT.format(
        transcript=transcript or 'No transcript provided - generate based on typical budget myths',
        priority_claims=claims_text or 'No specific claims provided - focus on common MMT myths'
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

        # Extract text from response
        response_text = message.content[0].text if message.content else ''

        # Parse JSON response
        rebuttal_data = json.loads(response_text)

        return {
            'sections': rebuttal_data if isinstance(rebuttal_data, list) else []
        }

    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            'sections': [
                {
                    'title': 'Rebuttal Content',
                    'content': response_text if 'response_text' in locals() else 'Error generating response',
                    'order': 1
                }
            ]
        }
    except Exception as e:
        raise Exception(f"Error calling Claude API: {str(e)}")
