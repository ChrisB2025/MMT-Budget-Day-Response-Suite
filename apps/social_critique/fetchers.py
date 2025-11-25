"""URL content fetching services for social media platforms"""
import re
import hashlib
import logging
from datetime import timedelta
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlunparse

from django.utils import timezone

logger = logging.getLogger(__name__)

# Nitter instances for Twitter/X proxy (in order of preference)
# Updated list - many instances go down frequently
NITTER_INSTANCES = [
    'nitter.privacydev.net',
    'nitter.poast.org',
    'nitter.woodland.cafe',
    'nitter.esmailelbob.xyz',
    'nitter.d420.de',
    'n.opnxng.com',
]

# Twitter syndication API - more reliable fallback
TWITTER_SYNDICATION_URL = 'https://syndication.twitter.com/srv/timeline-profile/screen-name/'
TWITTER_PUBLISH_URL = 'https://publish.twitter.com/oembed'

# Site domain for shareable links
SITE_DOMAIN = 'mmtaction.uk'


# Platform character limits for replies
PLATFORM_CHAR_LIMITS = {
    'twitter': 280,
    'threads': 500,
    'bluesky': 300,
    'mastodon': 500,
    'linkedin': 3000,
    'facebook': 63206,
    'instagram': 2200,
    'tiktok': 2200,
    'youtube': 10000,
    'reddit': 10000,
    'other': 10000,
}


def get_url_hash(url: str) -> str:
    """Generate SHA256 hash of URL for caching"""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


def detect_platform(url: str) -> str:
    """Detect which social media platform a URL belongs to"""
    parsed = urlparse(url.lower())
    domain = parsed.netloc.replace('www.', '')

    platform_patterns = {
        'twitter': ['twitter.com', 'x.com', 't.co'],
        'youtube': ['youtube.com', 'youtu.be', 'm.youtube.com'],
        'facebook': ['facebook.com', 'fb.com', 'fb.watch', 'm.facebook.com'],
        'instagram': ['instagram.com', 'instagr.am'],
        'tiktok': ['tiktok.com', 'vm.tiktok.com'],
        'linkedin': ['linkedin.com', 'lnkd.in'],
        'threads': ['threads.net'],
        'bluesky': ['bsky.app', 'bsky.social'],
        'mastodon': ['mastodon.social', 'mastodon.online', 'mstdn.social'],
        'reddit': ['reddit.com', 'redd.it', 'old.reddit.com'],
    }

    for platform, domains in platform_patterns.items():
        for d in domains:
            if d in domain:
                return platform

    # Check for Mastodon instances (common patterns)
    if '/users/' in parsed.path or '/@' in parsed.path:
        return 'mastodon'

    return 'other'


def extract_youtube_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats"""
    parsed = urlparse(url)

    # youtu.be/VIDEO_ID
    if 'youtu.be' in parsed.netloc:
        return parsed.path.strip('/')

    # youtube.com/watch?v=VIDEO_ID
    if 'v' in parse_qs(parsed.query):
        return parse_qs(parsed.query)['v'][0]

    # youtube.com/embed/VIDEO_ID or youtube.com/v/VIDEO_ID
    match = re.match(r'^/(embed|v)/([^/?]+)', parsed.path)
    if match:
        return match.group(2)

    # youtube.com/shorts/VIDEO_ID
    if '/shorts/' in parsed.path:
        return parsed.path.split('/shorts/')[-1].split('/')[0]

    return None


def extract_twitter_post_id(url: str) -> Optional[str]:
    """Extract Twitter/X post ID from URL"""
    parsed = urlparse(url)

    # Match /status/POST_ID pattern
    match = re.search(r'/status/(\d+)', parsed.path)
    if match:
        return match.group(1)

    return None


def convert_twitter_to_nitter(url: str, nitter_instance: str = None) -> Tuple[str, str]:
    """
    Convert a Twitter/X URL to a Nitter URL for fetching.

    Args:
        url: Original Twitter/X URL
        nitter_instance: Specific Nitter instance to use (default: first available)

    Returns:
        Tuple of (nitter_url, original_url)
    """
    if nitter_instance is None:
        nitter_instance = NITTER_INSTANCES[0]

    parsed = urlparse(url)

    # Check if this is a Twitter/X URL
    domain = parsed.netloc.lower().replace('www.', '')
    if domain not in ['twitter.com', 'x.com', 'mobile.twitter.com', 'mobile.x.com']:
        return url, url  # Not a Twitter URL, return as-is

    # Replace the domain with Nitter
    nitter_url = urlunparse((
        'https',
        nitter_instance,
        parsed.path,
        parsed.params,
        '',  # Remove query params (they often break Nitter)
        ''   # Remove fragment
    ))

    return nitter_url, url


def convert_nitter_to_twitter(url: str) -> str:
    """
    Convert a Nitter URL back to Twitter URL.

    Args:
        url: Nitter URL

    Returns:
        Original Twitter URL
    """
    parsed = urlparse(url)

    # Check if this is a Nitter URL
    if not any(instance in parsed.netloc for instance in NITTER_INSTANCES):
        return url  # Not a Nitter URL

    # Replace with Twitter
    twitter_url = urlunparse((
        'https',
        'x.com',
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    return twitter_url


def is_twitter_url(url: str) -> bool:
    """Check if URL is a Twitter/X URL"""
    parsed = urlparse(url.lower())
    domain = parsed.netloc.replace('www.', '')
    return domain in ['twitter.com', 'x.com', 'mobile.twitter.com', 'mobile.x.com', 't.co']


def fetch_twitter_oembed(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    """
    Fetch Twitter content using the official oEmbed API.
    This is more reliable than scraping Nitter.

    Returns dict with author_name, author_url, html (contains tweet text)
    """
    try:
        import requests
        import re

        # Normalize URL to use twitter.com (oEmbed requires it)
        normalized_url = url.replace('x.com', 'twitter.com')

        oembed_url = f"{TWITTER_PUBLISH_URL}?url={normalized_url}&omit_script=true"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }

        response = requests.get(oembed_url, headers=headers, timeout=timeout)

        if response.status_code == 200:
            data = response.json()

            # Extract text from HTML
            html_content = data.get('html', '')
            # Remove HTML tags to get plain text
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            # Remove "— Author (@handle) Date" suffix
            text = re.sub(r'\s*—\s*[^—]+\(@\w+\)\s*\w+\s*\d+,\s*\d+\s*$', '', text)

            return {
                'author': data.get('author_name', ''),
                'author_url': data.get('author_url', ''),
                'text': text,
                'html': html_content,
            }
        else:
            logger.warning(f"Twitter oEmbed failed with status {response.status_code}")
            return None

    except Exception as e:
        logger.warning(f"Twitter oEmbed error: {e}")
        return None


def fetch_twitter_content(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch Twitter/X content using multiple methods:
    1. Try oEmbed API (most reliable)
    2. Try Nitter instances
    3. Fall back to basic meta tags from Twitter

    Returns standardized content dict
    """
    import requests
    from bs4 import BeautifulSoup

    result = {
        'platform': 'twitter',
        'title': '',
        'author': '',
        'text': '',
        'description': '',
        'thumbnail_url': '',
        'publish_date': None,
        'original_url': url,
        'error': None,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    # Method 1: Try oEmbed API first (most reliable)
    logger.info(f"Trying Twitter oEmbed for {url}")
    oembed_data = fetch_twitter_oembed(url, timeout=timeout)

    if oembed_data and oembed_data.get('text'):
        result['author'] = oembed_data.get('author', '')
        result['text'] = oembed_data.get('text', '')
        result['title'] = f"Tweet by {result['author']}" if result['author'] else "Tweet"
        result['description'] = result['text'][:300] if result['text'] else ''
        logger.info(f"Successfully fetched via oEmbed: {result['text'][:100]}...")
        return result

    # Method 2: Try Nitter instances
    logger.info(f"oEmbed failed, trying Nitter instances")
    for nitter_instance in NITTER_INSTANCES:
        try:
            nitter_url, _ = convert_twitter_to_nitter(url, nitter_instance)
            logger.info(f"Trying Nitter instance: {nitter_instance}")

            response = requests.get(nitter_url, headers=headers, timeout=timeout, allow_redirects=True)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Try multiple Nitter content selectors
                tweet_text = None

                # Primary: tweet-content class
                tweet_content = soup.find('div', class_='tweet-content')
                if tweet_content:
                    tweet_text = tweet_content.get_text(strip=True)

                # Alternative: main-tweet container
                if not tweet_text:
                    main_tweet = soup.find('div', class_='main-tweet')
                    if main_tweet:
                        content = main_tweet.find('div', class_='tweet-content')
                        if content:
                            tweet_text = content.get_text(strip=True)

                # Alternative: timeline-item
                if not tweet_text:
                    timeline_item = soup.find('div', class_='timeline-item')
                    if timeline_item:
                        content = timeline_item.find('div', class_='tweet-content')
                        if content:
                            tweet_text = content.get_text(strip=True)

                if tweet_text and len(tweet_text) > 20:
                    # Get author
                    author_elem = soup.find('a', class_='fullname')
                    if author_elem:
                        result['author'] = author_elem.get_text(strip=True)

                    result['text'] = tweet_text
                    result['title'] = f"Tweet by {result['author']}" if result['author'] else "Tweet"
                    result['description'] = tweet_text[:300]

                    # Try to get avatar/image
                    avatar = soup.find('img', class_='avatar')
                    if avatar:
                        result['thumbnail_url'] = avatar.get('src', '')

                    logger.info(f"Successfully fetched via Nitter ({nitter_instance}): {tweet_text[:100]}...")
                    return result
                else:
                    logger.warning(f"Nitter {nitter_instance} returned no useful content")

        except requests.exceptions.Timeout:
            logger.warning(f"Nitter {nitter_instance} timed out")
        except Exception as e:
            logger.warning(f"Nitter {nitter_instance} error: {e}")

        continue

    # Method 3: Last resort - try Twitter directly (usually blocked but worth trying)
    logger.info("All Nitter instances failed, trying Twitter directly")
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                result['description'] = og_desc.get('content', '')
                result['text'] = result['description']

            og_title = soup.find('meta', property='og:title')
            if og_title:
                result['title'] = og_title.get('content', '')
                # Extract author from title like "Author on X: ..."
                if ' on X:' in result['title'] or ' on Twitter:' in result['title']:
                    result['author'] = result['title'].split(' on ')[0]

            og_image = soup.find('meta', property='og:image')
            if og_image:
                result['thumbnail_url'] = og_image.get('content', '')

            if result['text']:
                logger.info(f"Got content from Twitter directly: {result['text'][:100]}...")
                return result
    except Exception as e:
        logger.warning(f"Direct Twitter fetch error: {e}")

    result['error'] = 'Could not fetch Twitter content. All methods failed (oEmbed, Nitter instances, direct).'
    return result


def fetch_url_content(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch content from a URL and extract relevant information.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Dictionary containing:
            - platform: Detected platform name
            - title: Page/post title
            - author: Author/channel name
            - text: Main text content
            - description: Meta description
            - thumbnail_url: Thumbnail/preview image
            - publish_date: Publication date if available
            - original_url: The original URL (important for Twitter/Nitter conversion)
            - error: Error message if fetch failed
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {
            'error': 'Required packages not installed. Run: pip install requests beautifulsoup4',
            'platform': detect_platform(url)
        }

    platform = detect_platform(url)
    original_url = url  # Store original URL

    # For Twitter/X URLs, use dedicated Twitter fetcher
    if is_twitter_url(url):
        logger.info(f"Detected Twitter URL, using dedicated fetcher: {url}")
        return fetch_twitter_content(url, timeout=timeout)

    result = {
        'platform': platform,
        'title': '',
        'author': '',
        'text': '',
        'description': '',
        'thumbnail_url': '',
        'publish_date': None,
        'original_url': original_url,
        'error': None,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
    }

    fetch_url = url

    try:
        response = requests.get(fetch_url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract Open Graph metadata (widely used by social platforms)
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_site_name = soup.find('meta', property='og:site_name')

        # Twitter Card metadata
        twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
        twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        twitter_creator = soup.find('meta', attrs={'name': 'twitter:creator'})

        # Standard metadata
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_author = soup.find('meta', attrs={'name': 'author'})

        # Title extraction (priority order)
        result['title'] = (
            (og_title and og_title.get('content')) or
            (twitter_title and twitter_title.get('content')) or
            (soup.title and soup.title.string) or
            ''
        )

        # Description
        result['description'] = (
            (og_description and og_description.get('content')) or
            (twitter_description and twitter_description.get('content')) or
            (meta_description and meta_description.get('content')) or
            ''
        )

        # Author
        result['author'] = (
            (twitter_creator and twitter_creator.get('content')) or
            (meta_author and meta_author.get('content')) or
            (og_site_name and og_site_name.get('content')) or
            ''
        )

        # Thumbnail
        result['thumbnail_url'] = (
            (og_image and og_image.get('content')) or
            (twitter_image and twitter_image.get('content')) or
            ''
        )

        # Platform-specific text extraction
        result['text'] = _extract_platform_text(soup, platform, url)

        # Try to extract publish date
        result['publish_date'] = _extract_publish_date(soup)

    except requests.exceptions.Timeout:
        result['error'] = 'Request timed out. The page took too long to respond.'
    except requests.exceptions.ConnectionError:
        result['error'] = 'Connection error. Could not reach the URL.'
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            result['error'] = 'Page not found (404). The content may have been deleted.'
        elif e.response.status_code == 403:
            result['error'] = 'Access denied (403). The page may be private or restricted.'
        else:
            result['error'] = f'HTTP error {e.response.status_code}'
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        result['error'] = f'Error fetching content: {str(e)}'

    return result


def _extract_platform_text(soup, platform: str, url: str) -> str:
    """Extract main text content based on platform"""

    # YouTube - try to get video description
    if platform == 'youtube':
        # Look for structured data
        script = soup.find('script', type='application/ld+json')
        if script:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'description' in data:
                    return data['description']
            except:
                pass

        # Fallback to meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')

    # Twitter/X - use Nitter extraction or OG tags
    elif platform == 'twitter':
        # Check if this is a Nitter page (has tweet-content class)
        tweet_content = soup.find('div', class_='tweet-content')
        if tweet_content:
            return tweet_content.get_text(strip=True)

        # Try to find the main tweet text on Nitter
        main_tweet = soup.find('div', class_='main-tweet')
        if main_tweet:
            content = main_tweet.find('div', class_='tweet-content')
            if content:
                return content.get_text(strip=True)

        # Fallback to OG description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '')

    # Reddit
    elif platform == 'reddit':
        # Try to find post content
        post = soup.find('div', {'data-testid': 'post-container'})
        if post:
            text_elem = post.find('div', {'data-click-id': 'text'})
            if text_elem:
                return text_elem.get_text(strip=True)

        # Fallback to title
        title = soup.find('h1')
        if title:
            return title.get_text(strip=True)

    # LinkedIn
    elif platform == 'linkedin':
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '')

    # Generic extraction - try common patterns
    # Look for article content
    article = soup.find('article')
    if article:
        paragraphs = article.find_all('p')
        if paragraphs:
            return '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:10])

    # Try main content area
    main = soup.find('main')
    if main:
        paragraphs = main.find_all('p')
        if paragraphs:
            return '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:10])

    # Last resort - first few paragraphs
    paragraphs = soup.find_all('p')
    if paragraphs:
        return '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:5])

    return ''


def _extract_publish_date(soup) -> Optional[str]:
    """Try to extract publication date from page"""
    from dateutil import parser as date_parser

    # Common date meta tags
    date_tags = [
        ('meta', {'property': 'article:published_time'}),
        ('meta', {'property': 'og:article:published_time'}),
        ('meta', {'name': 'date'}),
        ('meta', {'name': 'publish_date'}),
        ('meta', {'name': 'DC.date.issued'}),
        ('time', {'itemprop': 'datePublished'}),
        ('time', {'datetime': True}),
    ]

    for tag, attrs in date_tags:
        elem = soup.find(tag, attrs)
        if elem:
            date_str = elem.get('content') or elem.get('datetime') or elem.string
            if date_str:
                try:
                    return date_parser.parse(date_str)
                except:
                    continue

    return None


def get_cached_content(url: str) -> Optional[Dict[str, Any]]:
    """Get content from cache if available and not expired"""
    from .models import ContentCache

    url_hash = get_url_hash(url)

    try:
        cache = ContentCache.objects.get(url_hash=url_hash)
        if not cache.is_expired:
            return cache.content
        else:
            # Clean up expired cache
            cache.delete()
    except ContentCache.DoesNotExist:
        pass

    return None


def cache_content(url: str, content: Dict[str, Any], cache_hours: int = 24) -> None:
    """Store content in cache"""
    from .models import ContentCache

    url_hash = get_url_hash(url)
    expires_at = timezone.now() + timedelta(hours=cache_hours)

    ContentCache.objects.update_or_create(
        url_hash=url_hash,
        defaults={
            'url': url,
            'content': content,
            'expires_at': expires_at,
        }
    )


def fetch_with_cache(url: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch URL content with caching support.

    First checks cache, then fetches if needed and caches result.
    """
    # Check cache first
    cached = get_cached_content(url)
    if cached:
        logger.info(f"Cache hit for URL: {url[:50]}")
        return cached

    # Fetch fresh content
    content = fetch_url_content(url, timeout)

    # Only cache successful fetches
    if not content.get('error'):
        cache_content(url, content)

    return content


def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate a URL for processing.

    Returns:
        Dictionary with:
            - valid: Boolean indicating if URL is valid
            - platform: Detected platform
            - error: Error message if invalid
    """
    result = {
        'valid': False,
        'platform': 'other',
        'error': None
    }

    # Basic URL validation
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

        # Detect platform
        result['platform'] = detect_platform(url)
        result['valid'] = True

    except Exception as e:
        result['error'] = f'Invalid URL: {str(e)}'

    return result
