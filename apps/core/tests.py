"""Tests for core app - MMT Campaign Suite refactor"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HomepageTests(TestCase):
    """Test the homepage renders correctly with new branding"""

    def setUp(self):
        self.client = Client()

    def test_homepage_renders(self):
        """Test homepage renders successfully"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_homepage_has_mmt_campaign_suite_h1(self):
        """Test homepage has new H1: MMT Campaign Suite"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'MMT Campaign Suite')

    def test_homepage_no_countdown(self):
        """Test homepage does not contain the Autumn Statement countdown"""
        response = self.client.get(reverse('core:home'))
        # Check that countdown elements are not present
        self.assertNotContains(response, 'countdown-days')
        self.assertNotContains(response, 'countdown-hours')
        self.assertNotContains(response, 'Autumn Statement')
        self.assertNotContains(response, '26 Nov 2025')

    def test_homepage_has_discord_link(self):
        """Test homepage contains Discord invite link"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'discord.gg')

    def test_homepage_has_campaign_tools(self):
        """Test homepage has the three campaign tool sections"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Social Media Target')
        self.assertContains(response, 'Article Target')
        self.assertContains(response, 'Complaint or Response')


class NavigationTests(TestCase):
    """Test navigation structure"""

    def setUp(self):
        self.client = Client()

    def test_navigation_has_campaigns_link(self):
        """Test navigation includes Campaigns link"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'href="/campaigns/"')

    def test_navigation_has_discord_link(self):
        """Test navigation includes Discord link"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'Discord')
        self.assertContains(response, 'discord.gg')

    def test_navigation_no_factcheck_link(self):
        """Test navigation does not include public Fact-Check link"""
        response = self.client.get(reverse('core:home'))
        # Should not have a direct link to factcheck in main navigation
        self.assertNotContains(response, 'href="/factcheck/"')

    def test_navigation_no_rebuttal_link(self):
        """Test navigation does not include public Rebuttal link"""
        response = self.client.get(reverse('core:home'))
        # Should not have a direct link to rebuttal in main navigation
        self.assertNotContains(response, 'href="/rebuttal/latest/"')


class CampaignsDashboardTests(TestCase):
    """Test campaigns dashboard"""

    def setUp(self):
        self.client = Client()

    def test_campaigns_page_renders(self):
        """Test campaigns page renders successfully"""
        response = self.client.get(reverse('core:campaigns'))
        self.assertEqual(response.status_code, 200)

    def test_campaigns_page_has_title(self):
        """Test campaigns page has correct title"""
        response = self.client.get(reverse('core:campaigns'))
        self.assertContains(response, 'Campaigns Dashboard')

    def test_campaigns_page_has_sections(self):
        """Test campaigns page has the expected sections"""
        response = self.client.get(reverse('core:campaigns'))
        self.assertContains(response, 'Social Media Targets')
        self.assertContains(response, 'Article Targets')
        self.assertContains(response, 'Active Complaints')


class RebuttalAccessTests(TestCase):
    """Test rebuttal is restricted to staff"""

    def setUp(self):
        self.client = Client()
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )

    def test_rebuttal_redirects_anonymous(self):
        """Test rebuttal page redirects anonymous users to login"""
        response = self.client.get(reverse('rebuttal:home'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_rebuttal_redirects_regular_user(self):
        """Test rebuttal page redirects regular users to login"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('rebuttal:home'))
        # Should redirect to login (staff_member_required redirects to admin login)
        self.assertEqual(response.status_code, 302)

    def test_rebuttal_accessible_to_staff(self):
        """Test rebuttal page is accessible to staff users"""
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('rebuttal:home'))
        self.assertEqual(response.status_code, 200)


class AboutHelpPagesTests(TestCase):
    """Test about and help pages have updated content"""

    def setUp(self):
        self.client = Client()

    def test_about_page_renders(self):
        """Test about page renders"""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_has_discord(self):
        """Test about page has Discord section"""
        response = self.client.get(reverse('core:about'))
        self.assertContains(response, 'Join the Community')
        self.assertContains(response, 'discord.gg')

    def test_about_page_has_keystroke_kingdom(self):
        """Test about page has Keystroke Kingdom section"""
        response = self.client.get(reverse('core:about'))
        self.assertContains(response, 'Keystroke Kingdom')
        self.assertContains(response, 'keystroke.mmtaction.uk')

    def test_help_page_renders(self):
        """Test help page renders"""
        response = self.client.get(reverse('core:help'))
        self.assertEqual(response.status_code, 200)

    def test_help_page_has_campaign_tools(self):
        """Test help page has campaign tools section"""
        response = self.client.get(reverse('core:help'))
        self.assertContains(response, 'Campaign Tools')

    def test_help_page_has_discord(self):
        """Test help page has Discord section"""
        response = self.client.get(reverse('core:help'))
        self.assertContains(response, 'discord.gg')


class FooterTests(TestCase):
    """Test footer has updated content"""

    def setUp(self):
        self.client = Client()

    def test_footer_has_mmt_campaign_suite(self):
        """Test footer has MMT Campaign Suite branding"""
        response = self.client.get(reverse('core:home'))
        self.assertContains(response, 'MMT Campaign Suite')

    def test_footer_no_budget_day_reference(self):
        """Test footer does not reference Budget Day 2025"""
        response = self.client.get(reverse('core:home'))
        self.assertNotContains(response, 'Budget Day 2025')
        self.assertNotContains(response, 'Autumn Statement 2025')
