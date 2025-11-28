"""Article extraction services with paywall bypass cascade."""
import hashlib
import logging
import re
from datetime import timedelta
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, quote

from django.utils import timezone

logger = logging.getLogger(__name__)

# Site domain for shareable links
SITE_DOMAIN = 'mmtaction.uk'

# Paywall detection phrases
PAYWALL_INDICATORS = [
    'subscribe to read',
    'subscription required',
    'premium content',
    'members only',
    'to continue reading',
    'sign up to read',
    'register to continue',
    'unlock this article',
    'exclusive content',
    'join to read',
    'become a member',
    'subscriber exclusive',
    'for subscribers only',
    'start your free trial',
    'already a subscriber',
]

# Article content selectors (priority order)
ARTICLE_SELECTORS = [
    'article',
    '[role="article"]',
    '.article-body',
    '.article-content',
    '.article__body',
    '.story-content',
    '.story-body',
    '.post-content',
    '.entry-content',
    '.content-body',
    '.main-content',
    '#article-body',
    '#story-body',
    '.article-text',
    '.article__content',
    '.c-article-body',
    '.js-article-body',
]

# Publication domain mapping
PUBLICATION_DOMAINS = {
    'theguardian.com': 'guardian',
    'bbc.co.uk': 'bbc',
    'bbc.com': 'bbc',
    'independent.co.uk': 'independent',
    'ft.com': 'ft',
    'thetimes.co.uk': 'times',
    'telegraph.co.uk': 'telegraph',
    'economist.com': 'economist',
    'spectator.co.uk': 'spectator',
    'newstatesman.com': 'newstatesman',
    'mirror.co.uk': 'mirror',
    'dailymail.co.uk': 'daily_mail',
    'express.co.uk': 'express',
    'news.sky.com': 'sky_news',
    'itv.com': 'itv_news',
    'reuters.com': 'reuters',
    'bloomberg.com': 'bloomberg',
    'wsj.com': 'wsj',
    'nytimes.com': 'nyt',
}

# Known paywalled sites
PAYWALLED_SITES = [
    'ft.com',
    'thetimes.co.uk',
    'telegraph.co.uk',
    'economist.com',
    'spectator.co.uk',
    'wsj.com',
    'bloomberg.com',
]


def get_url_hash(url: str) -> str:
    """Generate SHA256 hash of URL for caching."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


def detect_publication(url: str) -> str:
    """Detect publication from URL domain."""
    parsed = urlparse(url.lower())
    domain = parsed.netloc.replace('www.', '')

    for site_domain, publication in PUBLICATION_DOMAINS.items():
        if site_domain in domain:
            return publication

    return 'other'


def is_likely_paywalled(url: str) -> bool:
    """Check if URL is from a known paywalled site."""
    parsed = urlparse(url.lower())
    domain = parsed.netloc.replace('www.', '')

    for paywalled_domain in PAYWALLED_SITES:
        if paywalled_domain in domain:
            return True

    return False


def detect_paywall_in_content(text: str) -> bool:
    """Check if extracted content indicates a paywall."""
    text_lower = text.lower()

    for indicator in PAYWALL_INDICATORS:
        if indicator in text_lower:
            # Make sure we're not just matching in a byline or sidebar
            # Check if it's prominent (appears early in content)
            position = text_lower.find(indicator)
            if position < 500:  # Found in first 500 chars
                return True

    # Also check if content is suspiciously short
    if len(text.strip()) < 300:
        return True

    return False


def extract_article_text_from_soup(soup) -> str:
    """Extract article text from BeautifulSoup object using multiple selectors."""
    from bs4 import BeautifulSoup

    # Try each selector in priority order
    for selector in ARTICLE_SELECTORS:
        try:
            if selector.startswith('.') or selector.startswith('#') or selector.startswith('['):
                element = soup.select_one(selector)
            else:
                element = soup.find(selector)

            if element:
                # Get all paragraphs within the element
                paragraphs = element.find_all('p')
                if paragraphs:
                    text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                    if len(text) > 200:  # Minimum content threshold
                        return text
        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")
            continue

    # Fallback: get all paragraphs from the page
    all_paragraphs = soup.find_all('p')
    if all_paragraphs:
        text = '\n\n'.join(p.get_text(strip=True) for p in all_paragraphs[:20] if p.get_text(strip=True))
        return text

    return ''


def extract_metadata_from_soup(soup) -> Dict[str, Any]:
    """Extract article metadata from BeautifulSoup object."""
    metadata = {
        'title': '',
        'author': '',
        'description': '',
        'publication_date': None,
    }

    # Title
    og_title = soup.find('meta', property='og:title')
    if og_title:
        metadata['title'] = og_title.get('content', '')
    elif soup.title:
        metadata['title'] = soup.title.string or ''

    # Clean up title (remove " | Publication Name" suffixes)
    if metadata['title']:
        metadata['title'] = re.sub(r'\s*[|–-]\s*[^|–-]+$', '', metadata['title']).strip()

    # Author
    author_meta = soup.find('meta', attrs={'name': 'author'})
    if author_meta:
        metadata['author'] = author_meta.get('content', '')

    # Try article:author
    if not metadata['author']:
        article_author = soup.find('meta', property='article:author')
        if article_author:
            metadata['author'] = article_author.get('content', '')

    # Try JSON-LD
    if not metadata['author']:
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if 'author' in data:
                        author_data = data['author']
                        if isinstance(author_data, dict):
                            metadata['author'] = author_data.get('name', '')
                        elif isinstance(author_data, list) and author_data:
                            metadata['author'] = author_data[0].get('name', '') if isinstance(author_data[0], dict) else str(author_data[0])
                        elif isinstance(author_data, str):
                            metadata['author'] = author_data
            except Exception:
                continue

    # Description
    og_description = soup.find('meta', property='og:description')
    if og_description:
        metadata['description'] = og_description.get('content', '')
    else:
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            metadata['description'] = meta_description.get('content', '')

    # Publication date
    date_meta = soup.find('meta', property='article:published_time')
    if date_meta:
        try:
            from dateutil import parser as date_parser
            metadata['publication_date'] = date_parser.parse(date_meta.get('content', ''))
        except Exception:
            pass

    return metadata


def fetch_direct(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch article content directly from URL."""
    import requests
    from bs4 import BeautifulSoup

    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'is_paywalled': False,
        'error': None,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
    }

    try:
        logger.info(f"Fetching directly: {url}")
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        result['metadata'] = extract_metadata_from_soup(soup)

        # Extract article text
        text = extract_article_text_from_soup(soup)

        if text:
            result['text'] = text
            result['is_paywalled'] = detect_paywall_in_content(text)

            if result['is_paywalled']:
                logger.info(f"Paywall detected in direct fetch: {url}")
            else:
                result['success'] = True
                logger.info(f"Successfully fetched directly ({len(text)} chars): {url}")
        else:
            result['error'] = 'Could not extract article content'
            result['is_paywalled'] = is_likely_paywalled(url)

    except requests.exceptions.HTTPError as e:
        result['error'] = f'HTTP error: {e.response.status_code}'
    except requests.exceptions.Timeout:
        result['error'] = 'Request timed out'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection error'
    except Exception as e:
        result['error'] = f'Error: {str(e)}'
        logger.error(f"Direct fetch error for {url}: {e}")

    return result


def fetch_via_archive_ph(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch article content via archive.ph."""
    import requests
    from bs4 import BeautifulSoup

    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'archive_url': '',
        'is_paywalled': False,
        'error': None,
    }

    # Try archive.ph first (best for UK paywalled sites)
    archive_url = f"https://archive.ph/newest/{url}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        logger.info(f"Trying archive.ph for: {url}")
        response = requests.get(archive_url, headers=headers, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check if we got a search results page (no archive exists)
            if 'No results' in response.text or 'archive.ph/search' in response.url:
                result['error'] = 'No archive found'
                return result

            result['archive_url'] = response.url
            result['metadata'] = extract_metadata_from_soup(soup)
            text = extract_article_text_from_soup(soup)

            if text and len(text) > 300:
                result['text'] = text
                result['success'] = True
                logger.info(f"Successfully fetched via archive.ph ({len(text)} chars)")
            else:
                result['error'] = 'Archive found but content too short'
        else:
            result['error'] = f'Archive returned status {response.status_code}'

    except Exception as e:
        result['error'] = f'archive.ph error: {str(e)}'
        logger.error(f"archive.ph error for {url}: {e}")

    return result


def fetch_via_removepaywall(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch article content via RemovePaywall service."""
    import requests
    from bs4 import BeautifulSoup

    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'archive_url': '',
        'is_paywalled': False,
        'error': None,
    }

    encoded_url = quote(url, safe='')
    removepaywall_url = f"https://www.removepaywall.com/search?url={encoded_url}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        logger.info(f"Trying RemovePaywall for: {url}")
        response = requests.get(removepaywall_url, headers=headers, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            result['archive_url'] = removepaywall_url
            result['metadata'] = extract_metadata_from_soup(soup)
            text = extract_article_text_from_soup(soup)

            if text and len(text) > 300:
                result['text'] = text
                result['success'] = True
                logger.info(f"Successfully fetched via RemovePaywall ({len(text)} chars)")
            else:
                result['error'] = 'RemovePaywall returned insufficient content'
        else:
            result['error'] = f'RemovePaywall returned status {response.status_code}'

    except Exception as e:
        result['error'] = f'RemovePaywall error: {str(e)}'
        logger.error(f"RemovePaywall error for {url}: {e}")

    return result


def fetch_via_wayback(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch article content via Wayback Machine."""
    import requests
    from bs4 import BeautifulSoup

    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'archive_url': '',
        'is_paywalled': False,
        'error': None,
    }

    # First check if URL is archived
    check_url = f"https://archive.org/wayback/available?url={quote(url, safe='')}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }

    try:
        logger.info(f"Checking Wayback Machine for: {url}")
        check_response = requests.get(check_url, headers=headers, timeout=15)
        check_data = check_response.json()

        if check_data.get('archived_snapshots', {}).get('closest'):
            archive_url = check_data['archived_snapshots']['closest']['url']

            # Fetch the archived page
            logger.info(f"Fetching from Wayback: {archive_url}")
            response = requests.get(archive_url, headers=headers, timeout=timeout, allow_redirects=True)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                result['archive_url'] = archive_url
                result['metadata'] = extract_metadata_from_soup(soup)
                text = extract_article_text_from_soup(soup)

                if text and len(text) > 300:
                    result['text'] = text
                    result['success'] = True
                    logger.info(f"Successfully fetched via Wayback ({len(text)} chars)")
                else:
                    result['error'] = 'Wayback archive content too short'
            else:
                result['error'] = f'Wayback returned status {response.status_code}'
        else:
            result['error'] = 'No Wayback archive found'

    except Exception as e:
        result['error'] = f'Wayback error: {str(e)}'
        logger.error(f"Wayback error for {url}: {e}")

    return result


def fetch_via_12ft(url: str, timeout: int = 30) -> Dict[str, Any]:
    """Fetch article content via 12ft.io."""
    import requests
    from bs4 import BeautifulSoup

    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'archive_url': '',
        'is_paywalled': False,
        'error': None,
    }

    twelve_ft_url = f"https://12ft.io/{url}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        logger.info(f"Trying 12ft.io for: {url}")
        response = requests.get(twelve_ft_url, headers=headers, timeout=timeout, allow_redirects=True)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check if 12ft.io was able to bypass
            if 'Unable to bypass' in response.text or '12ft has been disabled' in response.text:
                result['error'] = '12ft.io unable to bypass this paywall'
                return result

            result['archive_url'] = twelve_ft_url
            result['metadata'] = extract_metadata_from_soup(soup)
            text = extract_article_text_from_soup(soup)

            if text and len(text) > 300:
                result['text'] = text
                result['success'] = True
                logger.info(f"Successfully fetched via 12ft.io ({len(text)} chars)")
            else:
                result['error'] = '12ft.io returned insufficient content'
        else:
            result['error'] = f'12ft.io returned status {response.status_code}'

    except Exception as e:
        result['error'] = f'12ft.io error: {str(e)}'
        logger.error(f"12ft.io error for {url}: {e}")

    return result


def extract_article_with_cascade(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Extract article content using cascading fallback strategy.

    Order:
    1. Direct fetch (works for Guardian, BBC, Independent)
    2. archive.ph (best for FT, Times, Telegraph)
    3. RemovePaywall
    4. Wayback Machine
    5. 12ft.io

    Returns:
        Dictionary containing:
            - success: Boolean
            - text: Extracted article text
            - metadata: {title, author, description, publication_date}
            - extraction_method: Which method succeeded
            - archive_url: URL used for extraction (if archive)
            - is_paywalled: Whether paywall was detected
            - errors: List of errors from each method
    """
    result = {
        'success': False,
        'text': '',
        'metadata': {},
        'extraction_method': 'manual',
        'archive_url': '',
        'is_paywalled': False,
        'errors': [],
    }

    # Check if likely paywalled to optimize cascade order
    likely_paywalled = is_likely_paywalled(url)

    # Define extraction methods
    extraction_methods = [
        ('direct', fetch_direct),
        ('archive_ph', fetch_via_archive_ph),
        ('removepaywall', fetch_via_removepaywall),
        ('wayback', fetch_via_wayback),
        ('12ft', fetch_via_12ft),
    ]

    # For known paywalled sites, try archive first
    if likely_paywalled:
        extraction_methods = [
            ('archive_ph', fetch_via_archive_ph),
            ('direct', fetch_direct),
            ('removepaywall', fetch_via_removepaywall),
            ('wayback', fetch_via_wayback),
            ('12ft', fetch_via_12ft),
        ]

    for method_name, method_func in extraction_methods:
        try:
            logger.info(f"Trying extraction method: {method_name}")
            method_result = method_func(url, timeout=timeout)

            if method_result['success']:
                result['success'] = True
                result['text'] = method_result['text']
                result['metadata'] = method_result.get('metadata', {})
                result['extraction_method'] = method_name
                result['archive_url'] = method_result.get('archive_url', '')
                result['is_paywalled'] = method_result.get('is_paywalled', False)
                logger.info(f"Extraction succeeded with method: {method_name}")
                return result
            else:
                result['errors'].append({
                    'method': method_name,
                    'error': method_result.get('error', 'Unknown error')
                })
                # If direct fetch detected paywall, mark it
                if method_name == 'direct' and method_result.get('is_paywalled'):
                    result['is_paywalled'] = True

        except Exception as e:
            result['errors'].append({
                'method': method_name,
                'error': str(e)
            })
            logger.error(f"Extraction method {method_name} failed: {e}")

    # All methods failed
    logger.warning(f"All extraction methods failed for: {url}")
    return result


def get_cached_content(url: str) -> Optional[Dict[str, Any]]:
    """Get content from cache if available and not expired."""
    from .models import ArticleContentCache

    url_hash = get_url_hash(url)

    try:
        cache = ArticleContentCache.objects.get(url_hash=url_hash)
        if not cache.is_expired:
            return cache.content
        else:
            cache.delete()
    except ArticleContentCache.DoesNotExist:
        pass

    return None


def cache_content(url: str, content: Dict[str, Any], cache_hours: int = 24) -> None:
    """Store content in cache."""
    from .models import ArticleContentCache

    url_hash = get_url_hash(url)
    expires_at = timezone.now() + timedelta(hours=cache_hours)

    ArticleContentCache.objects.update_or_create(
        url_hash=url_hash,
        defaults={
            'url': url,
            'content': content,
            'expires_at': expires_at,
        }
    )


def extract_article_with_cache(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Extract article content with caching support.

    First checks cache, then extracts if needed and caches result.
    """
    # Check cache first
    cached = get_cached_content(url)
    if cached and cached.get('success') and cached.get('text'):
        logger.info(f"Cache hit for: {url}")
        return cached

    # Extract fresh content
    content = extract_article_with_cascade(url, timeout)

    # Only cache successful extractions
    if content.get('success') and content.get('text'):
        cache_content(url, content)

    return content


def validate_article_url(url: str) -> Dict[str, Any]:
    """
    Validate an article URL for processing.

    Returns:
        Dictionary with:
            - valid: Boolean
            - publication: Detected publication
            - error: Error message if invalid
    """
    result = {
        'valid': False,
        'publication': 'other',
        'error': None
    }

    if not url:
        result['error'] = 'URL is required'
        return result

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            result['error'] = 'URL must include http:// or https://'
            return result

        if parsed.scheme not in ['http', 'https']:
            result['error'] = 'URL must use http or https protocol'
            return result

        if not parsed.netloc:
            result['error'] = 'Invalid URL format'
            return result

        # Detect publication
        result['publication'] = detect_publication(url)
        result['valid'] = True

    except Exception as e:
        result['error'] = f'Invalid URL: {str(e)}'

    return result
