"""User views"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import RegisterForm, LoginForm
from .models import User


def register_view(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to the MMT Budget Response Suite!')
            return redirect('core:dashboard')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.display_name}!')
            return redirect(request.GET.get('next', 'core:dashboard'))
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile_view(request):
    """User profile"""
    return render(request, 'users/profile.html')


def setup_admin_view(request):
    """
    Temporary setup view to create admin superuser.
    Access at /setup-admin/ to create admin user with username 'admin' and password 'password'.
    This should be disabled or removed in production after initial setup.
    """
    # Check if admin user already exists
    if User.objects.filter(username='admin').exists():
        return HttpResponse(
            '<h1>Admin user already exists!</h1>'
            '<p>You can now <a href="/admin/">login to the admin panel</a>.</p>'
            '<p>Username: admin<br>Password: password</p>',
            content_type='text/html'
        )

    # Create admin superuser
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='',
            password='password',
            display_name='Admin'
        )
        return HttpResponse(
            '<h1>✅ Admin user created successfully!</h1>'
            '<p><a href="/admin/">Click here to login to the admin panel</a></p>'
            '<p>Username: <strong>admin</strong><br>Password: <strong>password</strong></p>'
            '<p style="color: orange;"><strong>⚠️ Important:</strong> Change this password after logging in!</p>',
            content_type='text/html'
        )
    except Exception as e:
        return HttpResponse(
            f'<h1>❌ Error creating admin user</h1><p>{str(e)}</p>',
            content_type='text/html',
            status=500
        )


def make_me_admin_view(request):
    """
    Temporary setup view to make current logged-in user a superuser.
    Access at /make-me-admin/ while logged in to gain admin privileges.
    This should be disabled or removed in production after initial setup.
    """
    if not request.user.is_authenticated:
        return HttpResponse(
            '<h1>⚠️ Not logged in</h1>'
            '<p>You must be logged in to use this feature.</p>'
            '<p><a href="/users/login/">Click here to login</a></p>',
            content_type='text/html'
        )

    user = request.user

    if user.is_superuser and user.is_staff:
        return HttpResponse(
            f'<h1>✅ You already have admin access!</h1>'
            f'<p>User <strong>{user.username}</strong> is already a superuser.</p>'
            f'<p><a href="/admin/">Click here to access the admin panel</a></p>',
            content_type='text/html'
        )

    try:
        # Make user a superuser and staff
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return HttpResponse(
            f'<h1>✅ Admin access granted!</h1>'
            f'<p>User <strong>{user.username}</strong> is now a superuser.</p>'
            f'<p><a href="/admin/">Click here to access the admin panel</a></p>'
            f'<p style="margin-top: 20px;">Now you can load the bingo phrases:</p>'
            f'<ol>'
            f'<li>Click the admin link above</li>'
            f'<li>Go to "Bingo Phrases"</li>'
            f'<li>Select the action "🎯 Load all Budget Day Bingo phrases"</li>'
            f'<li>Click "Go"</li>'
            f'</ol>',
            content_type='text/html'
        )
    except Exception as e:
        return HttpResponse(
            f'<h1>❌ Error granting admin access</h1><p>{str(e)}</p>',
            content_type='text/html',
            status=500
        )
