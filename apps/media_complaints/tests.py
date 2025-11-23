"""Comprehensive tests for media_complaints app"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from apps.users.models import User
from .models import (
    MediaOutlet, Complaint, ComplaintLetter,
    ComplaintStats, OutletSuggestion
)


class MediaOutletModelTest(TestCase):
    """Test MediaOutlet model"""

    def test_outlet_creation(self):
        """Test creating a media outlet"""
        outlet = MediaOutlet.objects.create(
            name="BBC News",
            media_type="tv",
            contact_email="complaints@bbc.co.uk",
            website="https://www.bbc.co.uk",
            regulator="Ofcom"
        )
        self.assertEqual(outlet.name, "BBC News")
        self.assertEqual(outlet.media_type, "tv")
        self.assertTrue(outlet.is_active)

    def test_outlet_str(self):
        """Test outlet string representation"""
        outlet = MediaOutlet.objects.create(
            name="The Guardian",
            media_type="print",
            contact_email="reader@guardian.co.uk"
        )
        self.assertIn("The Guardian", str(outlet))


class ComplaintModelTest(TestCase):
    """Test Complaint model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.outlet = MediaOutlet.objects.create(
            name="BBC News",
            media_type="tv",
            contact_email="complaints@bbc.co.uk"
        )

    def test_complaint_creation(self):
        """Test creating a complaint"""
        complaint = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="News at Six",
            presenter_journalist="Test Presenter",
            claim_description="Misleading claim about government debt",
            severity=4,
            preferred_tone="professional"
        )
        self.assertEqual(complaint.user, self.user)
        self.assertEqual(complaint.outlet, self.outlet)
        self.assertEqual(complaint.status, 'draft')

    def test_complaint_incident_hash_generation(self):
        """Test incident hash is generated on save"""
        complaint = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Test Show",
            presenter_journalist="Presenter",
            claim_description="Test claim"
        )
        self.assertNotEqual(complaint.incident_hash, '')
        self.assertEqual(complaint.complaint_number_for_incident, 1)

    def test_complaint_number_increments(self):
        """Test complaint number increments for same incident"""
        # Create first complaint
        complaint1 = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Same Show",
            presenter_journalist="Same Presenter",
            claim_description="Claim 1"
        )

        # Create second complaint for same incident
        complaint2 = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Same Show",
            presenter_journalist="Same Presenter",
            claim_description="Claim 2"
        )

        self.assertEqual(complaint1.complaint_number_for_incident, 1)
        self.assertEqual(complaint2.complaint_number_for_incident, 2)
        self.assertEqual(complaint1.incident_hash, complaint2.incident_hash)

    def test_complaint_str(self):
        """Test complaint string representation"""
        complaint = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Test Show",
            claim_description="Test claim"
        )
        self.assertIn(self.outlet.name, str(complaint))
        self.assertIn(self.user.display_name, str(complaint))


class ComplaintLetterModelTest(TestCase):
    """Test ComplaintLetter model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.outlet = MediaOutlet.objects.create(
            name="BBC News",
            media_type="tv",
            contact_email="complaints@bbc.co.uk"
        )
        self.complaint = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="News",
            claim_description="Test claim"
        )

    def test_letter_creation(self):
        """Test creating a complaint letter"""
        letter = ComplaintLetter.objects.create(
            complaint=self.complaint,
            subject="Complaint about misleading information",
            body="Dear Editor...",
            variation_strategy="correction",
            tone_used="professional",
            mmt_points_included=["point1", "point2"]
        )
        self.assertEqual(letter.complaint, self.complaint)
        self.assertEqual(letter.variation_strategy, "correction")
        self.assertEqual(len(letter.mmt_points_included), 2)

    def test_letter_mark_as_sent(self):
        """Test marking letter as sent"""
        letter = ComplaintLetter.objects.create(
            complaint=self.complaint,
            subject="Test",
            body="Body",
            variation_strategy="correction",
            tone_used="professional"
        )
        letter.mark_as_sent("complaints@bbc.co.uk")

        letter.refresh_from_db()
        self.complaint.refresh_from_db()

        self.assertIsNotNone(letter.sent_at)
        self.assertEqual(letter.sent_to_email, "complaints@bbc.co.uk")
        self.assertEqual(self.complaint.status, 'sent')

    def test_letter_str(self):
        """Test letter string representation"""
        letter = ComplaintLetter.objects.create(
            complaint=self.complaint,
            subject="Test",
            body="Body",
            variation_strategy="policy",
            tone_used="professional"
        )
        self.assertIn("policy", str(letter))


class ComplaintStatsModelTest(TestCase):
    """Test ComplaintStats model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.outlet = MediaOutlet.objects.create(
            name="BBC News",
            media_type="tv",
            contact_email="complaints@bbc.co.uk"
        )
        self.stats = ComplaintStats.objects.create(user=self.user)

    def test_stats_creation(self):
        """Test creating complaint stats"""
        self.assertEqual(self.stats.user, self.user)
        self.assertEqual(self.stats.total_complaints_filed, 0)
        self.assertEqual(self.stats.complaints_sent, 0)

    def test_stats_update(self):
        """Test updating stats"""
        # Create some complaints
        complaint1 = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Show 1",
            claim_description="Claim 1",
            status='draft'
        )
        complaint2 = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name="Show 2",
            claim_description="Claim 2",
            status='sent'
        )

        self.stats.update_stats()

        self.assertEqual(self.stats.total_complaints_filed, 2)
        self.assertEqual(self.stats.complaints_sent, 1)
        self.assertIsNotNone(self.stats.first_complaint_at)


class OutletSuggestionModelTest(TestCase):
    """Test OutletSuggestion model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

    def test_suggestion_creation(self):
        """Test creating an outlet suggestion"""
        suggestion = OutletSuggestion.objects.create(
            user=self.user,
            name="New Outlet",
            media_type="online",
            website="https://example.com",
            description="Should be added because..."
        )
        self.assertEqual(suggestion.user, self.user)
        self.assertEqual(suggestion.status, 'pending')

    def test_suggestion_str(self):
        """Test suggestion string representation"""
        suggestion = OutletSuggestion.objects.create(
            user=self.user,
            name="Suggested Outlet",
            media_type="radio"
        )
        self.assertIn("Suggested Outlet", str(suggestion))
        self.assertIn(self.user.display_name, str(suggestion))


class MediaComplaintsViewsTest(TestCase):
    """Test media complaints views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.outlet = MediaOutlet.objects.create(
            name="BBC News",
            media_type="tv",
            contact_email="complaints@bbc.co.uk"
        )

    def test_complaints_home_requires_login(self):
        """Test complaints home requires authentication"""
        response = self.client.get(reverse('media_complaints:home'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_complaints_home_loads(self):
        """Test complaints home loads for authenticated user"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('media_complaints:home'))
        self.assertEqual(response.status_code, 200)

    def test_submit_complaint_requires_login(self):
        """Test submitting a complaint requires authentication"""
        response = self.client.get(reverse('media_complaints:submit'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_my_complaints_view(self):
        """Test my complaints view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse('media_complaints:my_complaints'))
        self.assertEqual(response.status_code, 200)

    def test_community_complaints_view(self):
        """Test community complaints view"""
        response = self.client.get(reverse('media_complaints:community'))
        self.assertEqual(response.status_code, 200)

    def test_view_complaint(self):
        """Test viewing a specific complaint"""
        self.client.login(username="testuser", password="testpass123")
        complaint = Complaint.objects.create(
            user=self.user,
            outlet=self.outlet,
            incident_date=date.today(),
            programme_name='Test Show',
            claim_description='Misleading claim',
            severity=3
        )
        response = self.client.get(
            reverse('media_complaints:view_complaint', args=[complaint.id])
        )
        self.assertEqual(response.status_code, 200)
