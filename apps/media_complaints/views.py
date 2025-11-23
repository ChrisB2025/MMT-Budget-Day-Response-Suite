"""Views for media complaints"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone

from .models import Complaint, ComplaintLetter, MediaOutlet, ComplaintStats, OutletSuggestion
from .forms import ComplaintForm, OutletSuggestionForm
from .services import process_complaint_letter, send_complaint_email, get_or_create_complaint_stats, research_media_outlet

logger = logging.getLogger(__name__)


@login_required
def complaints_home(request):
    """Home page for media complaints with optimized queries"""
    # Get user's complaints with related data
    user_complaints = Complaint.objects.filter(
        user=request.user
    ).select_related('outlet', 'user').prefetch_related('letter')[:10]

    # Get statistics (use aggregation for efficiency)
    total_complaints = Complaint.objects.count()
    total_sent = Complaint.objects.filter(status='sent').count()

    # Get or create user stats
    user_stats = get_or_create_complaint_stats(request.user)

    # Get recent community complaints with all related data
    recent_complaints = Complaint.objects.filter(
        status__in=['generated', 'sent']
    ).select_related('user', 'outlet').prefetch_related('letter').order_by('-created_at')[:10]

    # Get most complained about outlets
    top_outlets = MediaOutlet.objects.annotate(
        complaint_count=Count('complaints')
    ).filter(complaint_count__gt=0).order_by('-complaint_count')[:5]

    context = {
        'user_complaints': user_complaints,
        'user_stats': user_stats,
        'total_complaints': total_complaints,
        'total_sent': total_sent,
        'recent_complaints': recent_complaints,
        'top_outlets': top_outlets,
    }

    return render(request, 'media_complaints/home.html', context)


@login_required
def submit_complaint(request):
    """Submit a new complaint"""
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.status = 'draft'
            complaint.save()

            messages.success(request, 'Complaint submitted! Generating your letter...')

            # Generate letter
            try:
                result = process_complaint_letter(complaint.id)
                if result['status'] == 'success':
                    messages.success(request, 'Letter generated successfully!')
                    return redirect('media_complaints:view_complaint', complaint_id=complaint.id)
                else:
                    messages.error(request, f'Error generating letter: {result.get("message", "Unknown error")}')
                    return redirect('media_complaints:view_complaint', complaint_id=complaint.id)
            except Exception as e:
                logger.error(f"Error generating letter for complaint {complaint.id}: {e}")
                messages.error(request, 'Error generating letter. You can try again from the complaint page.')
                return redirect('media_complaints:view_complaint', complaint_id=complaint.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ComplaintForm()

    context = {
        'form': form,
    }

    return render(request, 'media_complaints/submit.html', context)


@login_required
def view_complaint(request, complaint_id):
    """View a specific complaint and its letter"""
    complaint = get_object_or_404(
        Complaint.objects.select_related('outlet', 'user'),
        id=complaint_id
    )

    # Check if user owns this complaint
    is_owner = complaint.user == request.user

    # Get letter if it exists
    try:
        letter = complaint.letter
    except ComplaintLetter.DoesNotExist:
        letter = None

    context = {
        'complaint': complaint,
        'letter': letter,
        'is_owner': is_owner,
    }

    return render(request, 'media_complaints/detail.html', context)


@login_required
def regenerate_letter(request, complaint_id):
    """Regenerate a complaint letter"""
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    if request.method == 'POST':
        # Delete existing letter if any
        try:
            if hasattr(complaint, 'letter'):
                complaint.letter.delete()
        except ComplaintLetter.DoesNotExist:
            pass

        # Reset status
        complaint.status = 'draft'
        complaint.save()

        # Regenerate
        try:
            result = process_complaint_letter(complaint.id)
            if result['status'] == 'success':
                messages.success(request, 'Letter regenerated successfully!')
            else:
                messages.error(request, f'Error: {result.get("message")}')
        except Exception as e:
            logger.error(f"Error regenerating letter for complaint {complaint_id}: {e}")
            messages.error(request, 'Error regenerating letter. Please try again.')

    return redirect('media_complaints:view_complaint', complaint_id=complaint_id)


@login_required
def send_letter(request, complaint_id):
    """Mark letter as sent (user sends via their own email client)"""
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    if not hasattr(complaint, 'letter'):
        messages.error(request, 'No letter has been generated yet.')
        return redirect('media_complaints:view_complaint', complaint_id=complaint_id)

    if request.method == 'POST':
        # Just mark as sent - user will send via their email client
        letter = complaint.letter
        letter.sent_at = timezone.now()
        letter.sent_to_email = complaint.outlet.complaints_dept_email or complaint.outlet.contact_email
        letter.save()

        complaint.status = 'sent'
        complaint.save()

        # Update user stats
        user_stats = get_or_create_complaint_stats(request.user)
        user_stats.update_stats()

        messages.success(request, 'Marked as sent! Thank you for holding media accountable.')

        # Award gamification points (integrate with factcheck system if needed)
        # Could add: award_experience_points(request.user, 15, 'complaint_sent')

    return redirect('media_complaints:view_complaint', complaint_id=complaint_id)


@login_required
def my_complaints(request):
    """List user's complaints with optimized query"""
    complaints = Complaint.objects.filter(
        user=request.user
    ).select_related('outlet').prefetch_related('letter').order_by('-created_at')

    # Get user stats
    user_stats = get_or_create_complaint_stats(request.user)

    context = {
        'complaints': complaints,
        'user_stats': user_stats,
    }

    return render(request, 'media_complaints/my_complaints.html', context)


@login_required
def delete_complaint(request, complaint_id):
    """Delete a complaint (owner only)"""
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted.')
        return redirect('media_complaints:my_complaints')

    return redirect('media_complaints:view_complaint', complaint_id=complaint_id)


def community_complaints(request):
    """View all community complaints (public) with optimized queries"""
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    outlet_filter = request.GET.get('outlet', 'all')

    # Optimize query with select_related for foreign keys
    complaints = Complaint.objects.select_related('outlet', 'user').prefetch_related('letter')

    if status_filter != 'all':
        complaints = complaints.filter(status=status_filter)

    if outlet_filter != 'all':
        complaints = complaints.filter(outlet_id=outlet_filter)

    complaints = complaints.order_by('-created_at')

    # Get outlet list for filter (optimize with annotation)
    outlets = MediaOutlet.objects.annotate(
        complaint_count=Count('complaints')
    ).filter(complaint_count__gt=0).order_by('name')

    context = {
        'complaints': complaints,
        'outlets': outlets,
        'status_filter': status_filter,
        'outlet_filter': outlet_filter,
    }

    return render(request, 'media_complaints/community.html', context)


@login_required
def complaint_stats(request):
    """Statistics and analytics page"""
    # Overall stats
    total_complaints = Complaint.objects.count()
    total_sent = Complaint.objects.filter(status='sent').count()
    total_responses = ComplaintLetter.objects.filter(response_received=True).count()

    # By outlet
    outlet_stats = MediaOutlet.objects.annotate(
        total_complaints=Count('complaints'),
        sent_complaints=Count('complaints', filter=Q(complaints__status='sent'))
    ).filter(total_complaints__gt=0).order_by('-total_complaints')

    # By severity
    from django.db.models import Count as DjangoCount
    severity_stats = Complaint.objects.values('severity').annotate(
        count=DjangoCount('id')
    ).order_by('severity')

    # Top complainers (if public)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    top_users = User.objects.annotate(
        complaint_count=Count('media_complaints')
    ).filter(complaint_count__gt=0).order_by('-complaint_count')[:10]

    context = {
        'total_complaints': total_complaints,
        'total_sent': total_sent,
        'total_responses': total_responses,
        'outlet_stats': outlet_stats,
        'severity_stats': severity_stats,
        'top_users': top_users,
    }

    return render(request, 'media_complaints/stats.html', context)


@login_required
def preview_letter(request, complaint_id):
    """Preview letter as plain text (for copying)"""
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    if not hasattr(complaint, 'letter'):
        return JsonResponse({'error': 'No letter generated'}, status=404)

    letter = complaint.letter

    return render(request, 'media_complaints/letter_preview.html', {
        'complaint': complaint,
        'letter': letter,
    })


@login_required
def suggest_outlet(request):
    """Suggest a new media outlet"""
    if request.method == 'POST':
        form = OutletSuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.user = request.user
            suggestion.status = 'pending'
            suggestion.save()

            # Trigger AI research
            try:
                research_data = research_media_outlet(
                    outlet_name=suggestion.name,
                    media_type=suggestion.media_type,
                    website=suggestion.website
                )

                # Update suggestion with research results
                suggestion.suggested_contact_email = research_data['contact_email']
                suggestion.suggested_complaints_email = research_data['complaints_email']
                suggestion.suggested_regulator = research_data['regulator']
                suggestion.research_notes = research_data['notes']
                suggestion.status = 'researched'
                suggestion.save()

                messages.success(request, 'Outlet suggestion submitted! AI research completed.')
            except Exception as e:
                logger.error(f"Error researching outlet suggestion {suggestion.id}: {e}")
                messages.warning(request, 'Outlet suggested, but AI research failed. An admin will review manually.')

            return redirect('media_complaints:view_suggestion', suggestion_id=suggestion.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = OutletSuggestionForm()

    context = {
        'form': form,
    }

    return render(request, 'media_complaints/suggest_outlet.html', context)


@login_required
def view_suggestion(request, suggestion_id):
    """View an outlet suggestion"""
    suggestion = get_object_or_404(OutletSuggestion, id=suggestion_id)

    # Check if user is owner or staff
    is_owner = suggestion.user == request.user
    can_view = is_owner or request.user.is_staff

    if not can_view:
        messages.error(request, 'You do not have permission to view this suggestion.')
        return redirect('media_complaints:home')

    context = {
        'suggestion': suggestion,
        'is_owner': is_owner,
    }

    return render(request, 'media_complaints/suggestion_detail.html', context)


@login_required
def my_suggestions(request):
    """List user's outlet suggestions"""
    suggestions = OutletSuggestion.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'suggestions': suggestions,
    }

    return render(request, 'media_complaints/my_suggestions.html', context)
