"""Views for media complaints"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone

from .models import Complaint, ComplaintLetter, MediaOutlet, ComplaintStats
from .forms import ComplaintForm
from .services import process_complaint_letter, send_complaint_email, get_or_create_complaint_stats

logger = logging.getLogger(__name__)


@login_required
def complaints_home(request):
    """Home page for media complaints"""
    # Get user's complaints
    user_complaints = Complaint.objects.filter(user=request.user).select_related('outlet')[:10]

    # Get statistics
    total_complaints = Complaint.objects.count()
    total_sent = Complaint.objects.filter(status='sent').count()

    # Get or create user stats
    user_stats = get_or_create_complaint_stats(request.user)

    # Get recent community complaints
    recent_complaints = Complaint.objects.filter(
        status__in=['generated', 'sent']
    ).select_related('user', 'outlet').order_by('-created_at')[:10]

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
    """Send a complaint letter via email"""
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)

    if not hasattr(complaint, 'letter'):
        messages.error(request, 'No letter has been generated yet.')
        return redirect('media_complaints:view_complaint', complaint_id=complaint_id)

    if request.method == 'POST':
        try:
            result = send_complaint_email(complaint.letter.id)
            if result['status'] == 'success':
                messages.success(request, f'Letter sent to {result["sent_to"]}!')

                # Award gamification points (integrate with factcheck system if needed)
                # Could add: award_experience_points(request.user, 15, 'complaint_sent')

            else:
                messages.error(request, f'Error sending: {result.get("message")}')
        except Exception as e:
            logger.error(f"Error sending letter for complaint {complaint_id}: {e}")
            messages.error(request, 'Error sending letter. Please try again.')

    return redirect('media_complaints:view_complaint', complaint_id=complaint_id)


@login_required
def my_complaints(request):
    """List user's complaints"""
    complaints = Complaint.objects.filter(
        user=request.user
    ).select_related('outlet').order_by('-created_at')

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
    """View all community complaints (public)"""
    # Filter by status
    status_filter = request.GET.get('status', 'all')
    outlet_filter = request.GET.get('outlet', 'all')

    complaints = Complaint.objects.select_related('outlet', 'user')

    if status_filter != 'all':
        complaints = complaints.filter(status=status_filter)

    if outlet_filter != 'all':
        complaints = complaints.filter(outlet_id=outlet_filter)

    complaints = complaints.order_by('-created_at')

    # Get outlet list for filter
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
