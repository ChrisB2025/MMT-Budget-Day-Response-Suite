"""Comprehensive tests for users app"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Team, User
from .forms import RegisterForm, LoginForm


class TeamModelTest(TestCase):
    """Test Team model"""

    def test_team_creation(self):
        """Test creating a team"""
        team = Team.objects.create(name="Test Team")
        self.assertEqual(team.name, "Test Team")
        self.assertEqual(team.total_points, 0)
        self.assertIsNotNone(team.created_at)

    def test_team_str(self):
        """Test team string representation"""
        team = Team.objects.create(name="Test Team")
        self.assertEqual(str(team), "Test Team")


class UserModelTest(TestCase):
    """Test User model"""

    def setUp(self):
        """Set up test data"""
        self.team = Team.objects.create(name="Test Team")

    def test_user_creation(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.points, 0)
        self.assertTrue(user.check_password("testpass123"))

    def test_user_with_team(self):
        """Test creating a user with a team"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            team=self.team
        )
        self.assertEqual(user.team, self.team)
        self.assertIn(user, self.team.members.all())

    def test_user_display_name_auto_set(self):
        """Test that display_name is auto-set from username"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.assertEqual(user.display_name, "testuser")

    def test_user_display_name_custom(self):
        """Test setting custom display_name"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User"
        )
        self.assertEqual(user.display_name, "Test User")

    def test_user_str(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User"
        )
        self.assertEqual(str(user), "Test User")

    def test_superuser_creation(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class RegisterFormTest(TestCase):
    """Test RegisterForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_without_display_name(self):
        """Test form without display_name (optional field)"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_missing_email(self):
        """Test form without required email"""
        form_data = {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())


class LoginFormTest(TestCase):
    """Test LoginForm"""

    def setUp(self):
        """Set up test user"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_valid_login(self):
        """Test form with valid credentials"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_password(self):
        """Test form with invalid password"""
        form_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class RegisterViewTest(TestCase):
    """Test registration view"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('users:register')

    def test_register_page_loads(self):
        """Test that register page loads"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_successful_registration(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'display_name': 'New User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_redirects_if_authenticated(self):
        """Test that authenticated users are redirected"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect


class LoginViewTest(TestCase):
    """Test login view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.url = reverse('users:login')
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            display_name="Test User"
        )

    def test_login_page_loads(self):
        """Test that login page loads"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_successful_login(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_failed_login(self):
        """Test failed login with wrong password"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # Stay on page
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_redirects_if_authenticated(self):
        """Test that authenticated users are redirected"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect


class LogoutViewTest(TestCase):
    """Test logout view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.url = reverse('users:logout')
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_logout_requires_authentication(self):
        """Test that logout requires authentication"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_successful_logout(self):
        """Test successful logout"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class ProfileViewTest(TestCase):
    """Test profile view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.url = reverse('users:profile')
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_profile_requires_authentication(self):
        """Test that profile requires authentication"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_page_loads(self):
        """Test that profile page loads for authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')


class SetupAdminViewTest(TestCase):
    """Test setup admin view"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('users:setup_admin')

    def test_creates_admin_user(self):
        """Test that admin user is created"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='admin').exists())
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_does_not_recreate_admin(self):
        """Test that admin user is not recreated if exists"""
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='admin').count(), 1)


class MakeMeAdminViewTest(TestCase):
    """Test make me admin view"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.url = reverse('users:make_me_admin')
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_requires_authentication(self):
        """Test that view requires authentication"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Not logged in', response.content.decode())

    def test_makes_user_admin(self):
        """Test that user becomes admin"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_superuser)
        self.assertTrue(self.user.is_staff)

    def test_already_admin(self):
        """Test response when user is already admin"""
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('already have admin access', response.content.decode())
