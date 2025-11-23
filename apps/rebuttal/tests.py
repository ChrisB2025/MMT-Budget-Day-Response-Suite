"""Comprehensive tests for rebuttal app"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.users.models import User
from .models import Rebuttal, RebuttalSection


class RebuttalModelTest(TestCase):
    """Test Rebuttal model"""

    def test_rebuttal_creation(self):
        """Test creating a rebuttal"""
        rebuttal = Rebuttal.objects.create(
            title="Budget 2025 Rebuttal",
            version="1.0",
            published=False
        )
        self.assertEqual(rebuttal.title, "Budget 2025 Rebuttal")
        self.assertEqual(rebuttal.version, "1.0")
        self.assertFalse(rebuttal.published)
        self.assertIsNone(rebuttal.published_at)

    def test_rebuttal_str(self):
        """Test rebuttal string representation"""
        rebuttal = Rebuttal.objects.create(
            title="Test Rebuttal",
            version="2.5"
        )
        self.assertEqual(str(rebuttal), "Test Rebuttal (v2.5)")

    def test_rebuttal_published(self):
        """Test publishing a rebuttal"""
        rebuttal = Rebuttal.objects.create(
            title="Budget Rebuttal",
            published=True,
            published_at=timezone.now()
        )
        self.assertTrue(rebuttal.published)
        self.assertIsNotNone(rebuttal.published_at)


class RebuttalSectionModelTest(TestCase):
    """Test RebuttalSection model"""

    def setUp(self):
        """Set up test data"""
        self.rebuttal = Rebuttal.objects.create(
            title="Budget 2025 Rebuttal",
            version="1.0"
        )

    def test_section_creation(self):
        """Test creating a rebuttal section"""
        section = RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Introduction",
            content="This is the introduction...",
            section_order=1
        )
        self.assertEqual(section.rebuttal, self.rebuttal)
        self.assertEqual(section.title, "Introduction")
        self.assertEqual(section.section_order, 1)

    def test_section_str(self):
        """Test section string representation"""
        section = RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Myths Debunked",
            content="Content here",
            section_order=2
        )
        self.assertEqual(str(section), "Budget 2025 Rebuttal - Myths Debunked")

    def test_section_ordering(self):
        """Test sections are ordered correctly"""
        section3 = RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Conclusion",
            content="Conclusion",
            section_order=3
        )
        section1 = RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Introduction",
            content="Intro",
            section_order=1
        )
        section2 = RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Body",
            content="Body",
            section_order=2
        )

        sections = list(self.rebuttal.sections.all())
        self.assertEqual(sections[0], section1)
        self.assertEqual(sections[1], section2)
        self.assertEqual(sections[2], section3)


class RebuttalViewsTest(TestCase):
    """Test rebuttal views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.rebuttal = Rebuttal.objects.create(
            title="Test Rebuttal",
            version="1.0",
            published=True,
            published_at=timezone.now()
        )
        RebuttalSection.objects.create(
            rebuttal=self.rebuttal,
            title="Section 1",
            content="Content 1",
            section_order=1
        )

    def test_rebuttal_list_view(self):
        """Test rebuttal list view"""
        response = self.client.get(reverse('rebuttal:list'))
        self.assertEqual(response.status_code, 200)

    def test_rebuttal_detail_view(self):
        """Test rebuttal detail view"""
        response = self.client.get(
            reverse('rebuttal:detail', args=[self.rebuttal.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_rebuttal_download_requires_login(self):
        """Test rebuttal download requires authentication"""
        response = self.client.get(
            reverse('rebuttal:download', args=[self.rebuttal.id, 'pdf'])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login
