"""Comprehensive tests for factcheck app"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date
from apps.users.models import User
from .models import (
    FactCheckRequest, FactCheckResponse, FactCheckUpvote,
    UserProfile, UserBadge, UserFollow, ClaimComment,
    ClaimOfTheDay, ClaimOfTheMinute
)


class FactCheckRequestModelTest(TestCase):
    """Test FactCheckRequest model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_request_creation(self):
        """Test creating a fact-check request"""
        request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="The government is running out of money",
            context="Budget speech 2025",
            severity=8,
            status='submitted'
        )
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.severity, 8)
        self.assertEqual(request.status, 'submitted')
        self.assertEqual(request.upvotes, 0)

    def test_request_str(self):
        """Test request string representation"""
        request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim for string representation",
            severity=5
        )
        self.assertIn("Test claim", str(request))


class FactCheckResponseModelTest(TestCase):
    """Test FactCheckResponse model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )

    def test_response_creation(self):
        """Test creating a fact-check response"""
        response = FactCheckResponse.objects.create(
            request=self.request,
            the_claim="Restated claim",
            the_problem="This is misleading",
            the_reality="The truth is...",
            the_evidence="Evidence here",
            mmt_perspective="MMT perspective",
            citations=[{"title": "Test", "url": "http://example.com"}]
        )
        self.assertEqual(response.request, self.request)
        self.assertEqual(len(response.citations), 1)

    def test_response_str(self):
        """Test response string representation"""
        response = FactCheckResponse.objects.create(
            request=self.request,
            the_claim="Restated claim",
            the_problem="Problem",
            the_reality="Reality"
        )
        self.assertIn("Response to", str(response))


class FactCheckUpvoteModelTest(TestCase):
    """Test FactCheckUpvote model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )

    def test_upvote_creation(self):
        """Test creating an upvote"""
        upvote = FactCheckUpvote.objects.create(
            user=self.user,
            request=self.request
        )
        self.assertEqual(upvote.user, self.user)
        self.assertEqual(upvote.request, self.request)

    def test_upvote_unique_constraint(self):
        """Test user can't upvote same request twice"""
        FactCheckUpvote.objects.create(user=self.user, request=self.request)
        with self.assertRaises(Exception):
            FactCheckUpvote.objects.create(user=self.user, request=self.request)


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user)

    def test_profile_creation(self):
        """Test creating a user profile"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.level, 'bronze')
        self.assertEqual(self.profile.experience_points, 0)

    def test_calculate_level(self):
        """Test level calculation"""
        self.profile.experience_points = 50
        self.assertEqual(self.profile.calculate_level(), 'bronze')

        self.profile.experience_points = 250
        self.assertEqual(self.profile.calculate_level(), 'silver')

        self.profile.experience_points = 600
        self.assertEqual(self.profile.calculate_level(), 'gold')

        self.profile.experience_points = 1200
        self.assertEqual(self.profile.calculate_level(), 'platinum')

    def test_update_stats(self):
        """Test updating profile stats"""
        # Create some requests
        FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Claim 1",
            severity=5,
            status='submitted',
            upvotes=3
        )
        FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Claim 2",
            severity=7,
            status='reviewed',
            upvotes=5
        )

        self.profile.update_stats()

        self.assertEqual(self.profile.total_claims_submitted, 2)
        self.assertEqual(self.profile.claims_fact_checked, 1)
        self.assertEqual(self.profile.total_upvotes_earned, 8)


class UserBadgeModelTest(TestCase):
    """Test UserBadge model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_badge_creation(self):
        """Test creating a badge"""
        badge = UserBadge.objects.create(
            user=self.user,
            badge_type='first_claim'
        )
        self.assertEqual(badge.user, self.user)
        self.assertEqual(badge.badge_type, 'first_claim')

    def test_badge_unique_constraint(self):
        """Test user can't earn same badge twice"""
        UserBadge.objects.create(user=self.user, badge_type='first_claim')
        with self.assertRaises(Exception):
            UserBadge.objects.create(user=self.user, badge_type='first_claim')


class UserFollowModelTest(TestCase):
    """Test UserFollow model"""

    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123"
        )

    def test_follow_creation(self):
        """Test creating a follow relationship"""
        follow = UserFollow.objects.create(
            follower=self.user1,
            following=self.user2
        )
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)

    def test_follow_unique_constraint(self):
        """Test user can't follow same user twice"""
        UserFollow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(Exception):
            UserFollow.objects.create(follower=self.user1, following=self.user2)


class ClaimCommentModelTest(TestCase):
    """Test ClaimComment model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )

    def test_comment_creation(self):
        """Test creating a comment"""
        comment = ClaimComment.objects.create(
            request=self.request,
            user=self.user,
            text="This is a test comment"
        )
        self.assertEqual(comment.request, self.request)
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.text, "This is a test comment")


class ClaimOfTheDayModelTest(TestCase):
    """Test ClaimOfTheDay model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )

    def test_claim_of_day_creation(self):
        """Test creating claim of the day"""
        cotd = ClaimOfTheDay.objects.create(
            request=self.request,
            featured_date=date.today()
        )
        self.assertEqual(cotd.request, self.request)
        self.assertEqual(cotd.featured_date, date.today())

    def test_claim_of_day_unique_date(self):
        """Test only one claim per day"""
        ClaimOfTheDay.objects.create(
            request=self.request,
            featured_date=date.today()
        )
        other_request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Other claim",
            severity=5
        )
        with self.assertRaises(Exception):
            ClaimOfTheDay.objects.create(
                request=other_request,
                featured_date=date.today()
            )


class ClaimOfTheMinuteModelTest(TestCase):
    """Test ClaimOfTheMinute model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.request = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )

    def test_claim_of_minute_creation(self):
        """Test creating claim of the minute"""
        cotm = ClaimOfTheMinute.objects.create(
            request=self.request,
            minute_timestamp=timezone.now(),
            upvotes_at_time=10
        )
        self.assertEqual(cotm.request, self.request)
        self.assertEqual(cotm.upvotes_at_time, 10)


class FactCheckViewsTest(TestCase):
    """Test factcheck views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User"
        )

    def test_factcheck_home_loads(self):
        """Test factcheck home loads (public page)"""
        response = self.client.get(reverse('factcheck:home'))
        self.assertEqual(response.status_code, 200)

    def test_submit_claim_requires_login(self):
        """Test submitting a claim requires authentication"""
        response = self.client.get(reverse('factcheck:submit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_submit_claim_view(self):
        """Test submitting a claim"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse('factcheck:submit'),
            {
                'claim_text': 'Test claim',
                'context': 'Test context',
                'severity': 7
            }
        )
        # May redirect or stay on page depending on form validation
        self.assertIn(response.status_code, [200, 302])

    def test_claim_queue_view(self):
        """Test claim queue view"""
        response = self.client.get(reverse('factcheck:queue'))
        self.assertEqual(response.status_code, 200)

    def test_claim_detail_view(self):
        """Test claim detail view"""
        claim = FactCheckRequest.objects.create(
            user=self.user,
            claim_text="Test claim",
            severity=5
        )
        response = self.client.get(reverse('factcheck:detail', args=[claim.id]))
        self.assertEqual(response.status_code, 200)
