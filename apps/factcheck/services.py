"""Claude API service for fact-checking"""
import json
from django.conf import settings
from anthropic import Anthropic


# Prompt template for fact-checking
FACTCHECK_PROMPT = """You are an expert MMT economist reviewing a claim made during the UK Budget speech.

CLAIM: {claim_text}

CONTEXT: {context}

SEVERITY (user-rated 1-10): {severity}

Generate a structured fact-check with the following sections:

1. THE CLAIM: Restate the claim clearly and concisely
2. THE PROBLEM: Explain what is misleading about this framing (1-2 paragraphs)
3. THE REALITY: What is actually true about this situation (2-3 paragraphs)
4. THE EVIDENCE: Specific data, statistics, or sources that support the reality (bullet points with citations)
5. THE MMT PERSPECTIVE: How Modern Monetary Theory reframes this issue (2-3 paragraphs)

Use clear, accessible language. Cite specific sources where possible (ONS, Bank of England, academic papers). Be factual and evidence-based, not rhetorical.

Return as JSON with these exact keys: the_claim, the_problem, the_reality, the_evidence, mmt_perspective, citations (array of objects with title and url).

Important: Return ONLY valid JSON, no other text."""


def generate_fact_check_with_claude(claim, context='', severity=5):
    """
    Generate a fact-check response using Claude API.

    Args:
        claim: The claim text to fact-check
        context: Additional context (optional)
        severity: User-rated severity 1-10

    Returns:
        dict with fact-check data
    """
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = FACTCHECK_PROMPT.format(
        claim_text=claim,
        context=context or 'No additional context provided',
        severity=severity
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
        fact_check_data = json.loads(response_text)

        return {
            'the_claim': fact_check_data.get('the_claim', ''),
            'the_problem': fact_check_data.get('the_problem', ''),
            'the_reality': fact_check_data.get('the_reality', ''),
            'the_evidence': fact_check_data.get('the_evidence', ''),
            'mmt_perspective': fact_check_data.get('mmt_perspective', ''),
            'citations': fact_check_data.get('citations', [])
        }

    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            'the_claim': claim,
            'the_problem': 'Error parsing AI response',
            'the_reality': response_text if 'response_text' in locals() else 'Error generating response',
            'the_evidence': '',
            'mmt_perspective': '',
            'citations': []
        }
    except Exception as e:
        raise Exception(f"Error calling Claude API: {str(e)}")
