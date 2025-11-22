"""Rebuttal views"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Rebuttal
from .tasks import generate_rebuttal
from .exporters import export_as_markdown, export_as_html, export_as_pdf


def rebuttal_home(request):
    """Rebuttal home page"""
    latest_rebuttal = Rebuttal.objects.filter(published=True).first()

    return render(request, 'rebuttal/home.html', {
        'latest_rebuttal': latest_rebuttal
    })


def rebuttal_detail(request, rebuttal_id):
    """View a specific rebuttal"""
    rebuttal = get_object_or_404(
        Rebuttal.objects.prefetch_related('sections'),
        id=rebuttal_id
    )

    return render(request, 'rebuttal/detail.html', {
        'rebuttal': rebuttal
    })


def latest_rebuttal(request):
    """View the latest published rebuttal"""
    rebuttal = Rebuttal.objects.filter(published=True).first()

    if not rebuttal:
        return render(request, 'rebuttal/no_rebuttal.html')

    return redirect('rebuttal:detail', rebuttal_id=rebuttal.id)


@staff_member_required
def create_rebuttal(request):
    """Create a new rebuttal (admin only)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        version = request.POST.get('version', '1.0')
        transcript = request.POST.get('transcript', '')

        rebuttal = Rebuttal.objects.create(
            title=title,
            version=version
        )

        # Trigger async generation
        generate_rebuttal.delay(
            rebuttal_id=rebuttal.id,
            transcript=transcript
        )

        messages.success(
            request,
            'Rebuttal created! AI is generating content...'
        )
        return redirect('rebuttal:detail', rebuttal_id=rebuttal.id)

    return render(request, 'rebuttal/create.html')


@login_required
def download_rebuttal(request, rebuttal_id, format):
    """Download rebuttal in specified format"""
    rebuttal = get_object_or_404(Rebuttal, id=rebuttal_id)

    if format == 'markdown':
        return export_as_markdown(rebuttal)
    elif format == 'html':
        return export_as_html(rebuttal)
    elif format == 'pdf':
        return export_as_pdf(rebuttal)
    else:
        return HttpResponse('Invalid format', status=400)


def rebuttal_list(request):
    """List all rebuttals"""
    rebuttals = Rebuttal.objects.filter(published=True).order_by('-published_at')

    return render(request, 'rebuttal/list.html', {
        'rebuttals': rebuttals
    })
