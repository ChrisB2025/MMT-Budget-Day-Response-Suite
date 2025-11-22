"""Fact-check views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from django.db.models import Q
from .models import FactCheckRequest, FactCheckUpvote
from .forms import FactCheckSubmitForm
from .tasks import process_fact_check


def factcheck_home(request):
    """Fact-check home page"""
    recent_requests = FactCheckRequest.objects.filter(
        status__in=['reviewed', 'published']
    ).select_related('user', 'response').order_by('-created_at')[:10]

    return render(request, 'factcheck/home.html', {
        'recent_requests': recent_requests
    })


@login_required
def submit_factcheck(request):
    """Submit a new fact-check request"""
    if request.method == 'POST':
        form = FactCheckSubmitForm(request.POST)
        if form.is_valid():
            fact_check = form.save(commit=False)
            fact_check.user = request.user
            fact_check.save()

            # Trigger async processing
            process_fact_check.delay(fact_check.id)

            messages.success(
                request,
                'Fact-check request submitted! AI is generating a response...'
            )

            # For HTMX requests, return partial
            if request.headers.get('HX-Request'):
                return render(request, 'factcheck/partials/request_card.html', {
                    'request': fact_check
                })

            return redirect('factcheck:detail', request_id=fact_check.id)
    else:
        form = FactCheckSubmitForm()

    return render(request, 'factcheck/submit.html', {'form': form})


def factcheck_queue(request):
    """View queue of fact-check requests"""
    status_filter = request.GET.get('status', 'all')

    requests = FactCheckRequest.objects.select_related('user', 'response')

    if status_filter != 'all':
        requests = requests.filter(status=status_filter)

    requests = requests.order_by('-upvotes', '-created_at')

    # For HTMX pagination
    if request.headers.get('HX-Request'):
        return render(request, 'factcheck/partials/queue_list.html', {
            'requests': requests
        })

    return render(request, 'factcheck/queue.html', {
        'requests': requests,
        'status_filter': status_filter
    })


def factcheck_detail(request, request_id):
    """View a specific fact-check request and response"""
    fact_check = get_object_or_404(
        FactCheckRequest.objects.select_related('user', 'response'),
        id=request_id
    )

    has_upvoted = False
    if request.user.is_authenticated:
        has_upvoted = FactCheckUpvote.objects.filter(
            user=request.user,
            request=fact_check
        ).exists()

    return render(request, 'factcheck/detail.html', {
        'request': fact_check,
        'has_upvoted': has_upvoted
    })


@login_required
def upvote_factcheck(request, request_id):
    """Upvote a fact-check request"""
    if request.method != 'POST':
        return HttpResponse(status=405)

    fact_check = get_object_or_404(FactCheckRequest, id=request_id)

    # Toggle upvote
    upvote, created = FactCheckUpvote.objects.get_or_create(
        user=request.user,
        request=fact_check
    )

    if not created:
        # User already upvoted, remove it
        upvote.delete()
        fact_check.upvotes -= 1
        fact_check.save()
        has_upvoted = False
    else:
        # New upvote
        fact_check.upvotes += 1
        fact_check.save()
        has_upvoted = True

    # Return updated upvote button for HTMX
    return render(request, 'factcheck/partials/upvote_button.html', {
        'request': fact_check,
        'has_upvoted': has_upvoted
    })


def factcheck_stats(request):
    """Fact-check statistics"""
    total_submitted = FactCheckRequest.objects.count()
    total_answered = FactCheckRequest.objects.filter(
        status__in=['reviewed', 'published']
    ).count()

    avg_severity = FactCheckRequest.objects.aggregate(
        models.Avg('severity')
    )['severity__avg'] or 0

    top_contributors = FactCheckRequest.objects.values(
        'user__display_name'
    ).annotate(
        count=models.Count('id')
    ).order_by('-count')[:10]

    return render(request, 'factcheck/stats.html', {
        'total_submitted': total_submitted,
        'total_answered': total_answered,
        'avg_severity': round(avg_severity, 1),
        'top_contributors': top_contributors
    })
