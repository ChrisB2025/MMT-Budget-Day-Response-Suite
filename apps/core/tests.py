"""Comprehensive tests for core app"""
from django.test import TestCase, Client
from django.urls import reverse
from apps.users.models import User
from .models import UserAction, Achievement


class UserActionModelTest(TestCase):
    """Test UserAction model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_action_creation(self):
        """Test creating a user action"""
        action = UserAction.objects.create(
            user=self.user,
            action_type='bingo_mark',
            action_target='square_123',
            points_earned=10
        )
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.action_type, 'bingo_mark')
        self.assertEqual(action.points_earned, 10)

    def test_action_str(self):
        """Test action string representation"""
        action = UserAction.objects.create(
            user=self.user,
            action_type='factcheck_submit'
        )
        self.assertIn(self.user.display_name, str(action))
        self.assertIn('factcheck_submit', str(action))


class AchievementModelTest(TestCase):
    """Test Achievement model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_achievement_creation(self):
        """Test creating an achievement"""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_type='early_bird',
            achievement_data={'detail': 'First to complete'}
        )
        self.assertEqual(achievement.user, self.user)
        self.assertEqual(achievement.achievement_type, 'early_bird')
        self.assertEqual(achievement.achievement_data['detail'], 'First to complete')

    def test_achievement_unique_constraint(self):
        """Test user can't earn same achievement twice"""
        Achievement.objects.create(
            user=self.user,
            achievement_type='early_bird'
        )
        with self.assertRaises(Exception):
            Achievement.objects.create(
                user=self.user,
                achievement_type='early_bird'
            )

    def test_achievement_str(self):
        """Test achievement string representation"""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_type='bingo_champion'
        )
        self.assertIn(self.user.display_name, str(achievement))
        self.assertIn('bingo_champion', str(achievement))


class CoreViewsTest(TestCase):
    """Test core views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_home_view(self):
        """Test home page loads"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_loads_for_authenticated_user(self):
        """Test dashboard loads for authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
