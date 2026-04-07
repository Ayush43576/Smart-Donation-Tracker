from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from .models import NGO, Need, Donation, UtilizationReport
import uuid
from decimal import Decimal

def home(request):
    ngos = NGO.objects.filter(status='approved')[:6]
    needs = Need.objects.filter(is_active=True, ngo__status='approved').order_by('-id')[:4]
    total_donated = Donation.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    total_donors = Donation.objects.filter(status='completed').values('donor').distinct().count()
    total_ngos = NGO.objects.filter(status='approved').count()
    total_beneficiaries = UtilizationReport.objects.aggregate(t=Sum('beneficiaries_count'))['t'] or 0
    reports = UtilizationReport.objects.order_by('-submitted_at')[:3]
    return render(request, 'home.html', {
        'ngos': ngos, 'needs': needs,
        'total_donated': total_donated, 'total_donors': total_donors,
        'total_ngos': total_ngos, 'total_beneficiaries': total_beneficiaries,
        'reports': reports,
    })

def about(request):
    return render(request, 'about.html')

def ngo_list(request):
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    ngos = NGO.objects.filter(status='approved')
    if category:
        ngos = ngos.filter(category=category)
    if search:
        ngos = ngos.filter(name__icontains=search)
    categories = NGO.CATEGORY_CHOICES
    return render(request, 'ngo_list.html', {'ngos': ngos, 'categories': categories, 'selected_cat': category, 'search': search})

def ngo_detail(request, ngo_id):
    ngo = get_object_or_404(NGO, id=ngo_id, status='approved')
    needs = ngo.needs.filter(is_active=True)
    donations = ngo.donations.filter(status='completed', anonymous=False).order_by('-created_at')[:5]
    reports = ngo.reports.order_by('-submitted_at')[:3]
    return render(request, 'ngo_detail.html', {'ngo': ngo, 'needs': needs, 'donations': donations, 'reports': reports})

def donate(request, ngo_id=None):
    """Step 1: Choose NGO + amount"""
    ngos = NGO.objects.filter(status='approved')
    selected_ngo = None
    if ngo_id:
        selected_ngo = get_object_or_404(NGO, id=ngo_id, status='approved')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            # Save intent in session and redirect to login
            request.session['donate_post'] = dict(request.POST)
            messages.info(request, 'Please login to continue with your donation.')
            return redirect('/login/?next=/checkout/')

        # Store donation details in session for checkout
        request.session['pending_donation'] = {
            'ngo_id': request.POST.get('ngo_id'),
            'amount': request.POST.get('amount', '0'),
            'donation_type': request.POST.get('donation_type', 'monetary'),
            'message': request.POST.get('message', ''),
            'anonymous': request.POST.get('anonymous') == 'on',
            'material_description': request.POST.get('material_description', ''),
        }
        return redirect('checkout')

    return render(request, 'donate.html', {'ngos': ngos, 'selected_ngo': selected_ngo})

@login_required
def checkout(request):
    """Step 2: Secure payment page"""
    pending = request.session.get('pending_donation')
    if not pending:
        return redirect('donate')

    ngo = get_object_or_404(NGO, id=pending['ngo_id'], status='approved')

    if request.method == 'POST':
        # Validate card fields (mock)
        card_number = request.POST.get('card_number', '').replace(' ', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')

        if len(card_number) < 16 or not expiry or not cvv:
            messages.error(request, 'Please fill in all payment details correctly.')
            return render(request, 'checkout.html', {'ngo': ngo, 'pending': pending})

        # Create donation record
        dtype = pending.get('donation_type', 'monetary')
        amount = Decimal(pending.get('amount', '0')) if dtype == 'monetary' else Decimal('0')
        txn_id = str(uuid.uuid4())[:12].upper()

        donation = Donation.objects.create(
            donor=request.user,
            ngo=ngo,
            donation_type=dtype,
            amount=amount,
            message=pending.get('message', ''),
            anonymous=pending.get('anonymous', False),
            status='completed',
            transaction_id=txn_id,
        )

        # Clear session
        del request.session['pending_donation']

        # Store success info in session for the success page
        request.session['last_donation'] = {
            'txn_id': txn_id,
            'ngo_name': ngo.name,
            'ngo_initial': ngo.logo_initial,
            'amount': str(amount),
            'dtype': dtype,
            'donor': request.user.username,
            'donation_id': donation.id,
        }
        return redirect('payment_success')

    return render(request, 'checkout.html', {'ngo': ngo, 'pending': pending})

@login_required
def payment_success(request):
    """Step 3: Glorious success page"""
    info = request.session.get('last_donation')
    if not info:
        return redirect('home')
    # Don't clear immediately — let them read it
    return render(request, 'payment_success.html', {'info': info})

@login_required
def dashboard(request):
    donations = request.user.donations.all().order_by('-created_at')
    total = donations.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    ngos_supported = donations.values('ngo').distinct().count()
    return render(request, 'dashboard.html', {
        'donations': donations, 'total': total, 'ngos_supported': ngos_supported
    })

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'Welcome, {username}! Account created.')
            return redirect('home')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def api_stats(request):
    total = Donation.objects.filter(status='completed').aggregate(t=Sum('amount'))['t'] or 0
    return JsonResponse({
        'total_donated': float(total),
        'total_donors': Donation.objects.values('donor').distinct().count(),
        'total_ngos': NGO.objects.filter(status='approved').count(),
    })
