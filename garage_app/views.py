from collections import defaultdict
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, CreateView, TemplateView

from garage_app.forms import CarForm, MaintenanceRequestForm, ReviewForm, ProfileUpdateForm, CustomUserCreationForm
from garage_app.models import Car, MaintenanceRequest, Review, ServiceType


# Home View
def home_view(request):
    reviews = Review.objects.select_related('request', 'user').order_by('-created_at')[:3]  # latest 3 reviews
    return render(request, 'home.html', {'reviews': reviews})


# User Registration View
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# Car Edit View
@login_required
def car_edit_view(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            return redirect('car-list')
    else:
        form = CarForm(instance=car)
    return render(request, 'car_form.html', {'form': form, 'edit_mode': True})


# Car Delete View
@login_required
def car_delete_view(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    if request.method == 'POST':
        car.delete()
        return redirect('car-list')
    return render(request, 'car_confirm_delete.html', {'car': car})


# Staff View to Manage Requests
@staff_member_required
def manage_requests_view(request):
    requests = MaintenanceRequest.objects.select_related('car', 'service').all()
    return render(request, 'manage_requests.html', {'requests': requests})


# Staff Dashboard View
@staff_member_required
def staff_dashboard_view(request):
    requests = MaintenanceRequest.objects.select_related('car', 'service', 'car__owner').order_by('-requested_date')
    status_choices = MaintenanceRequest._meta.get_field('status').choices

    if request.method == 'POST':
        req_id = request.POST.get("request_id")
        new_status = request.POST.get("status")
        is_approved = "is_approved" in request.POST

        try:
            req = MaintenanceRequest.objects.select_related('car', 'service').get(id=req_id)
        except MaintenanceRequest.DoesNotExist:
            return redirect("staff-dashboard")

        req.status = new_status
        req.is_approved = is_approved
        req.save()

        # Update car with upgrade and horsepower if completed and approved
        if new_status == "Completed" and is_approved and req.service and req.service.category != "Basic Maintenance":
            upgrade_line = f"- {req.service.name} ({timezone.now().date()})"
            car = req.car

            if car.upgrades and upgrade_line not in car.upgrades:
                car.upgrades += f"\n{upgrade_line}"
            else:
                car.upgrades = upgrade_line

            if req.service.hp_gain:
                car.horsepower = (car.horsepower or 0) + req.service.hp_gain

            car.save()

        return redirect("staff-dashboard")

    return render(request, 'staff_dashboard.html', {'requests': requests, 'status_choices': status_choices})


# Request Edit View
@login_required
def request_edit_view(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk, car__owner=request.user)

    if req.status != 'Pending' or req.is_approved:
        messages.warning(request, "You can't edit this request. It’s already being processed.")
        return redirect('request-list')

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=req, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Request updated successfully.")
            return redirect('request-list')
    else:
        form = MaintenanceRequestForm(instance=req, user=request.user)

    # Group services by category
    services_by_category = defaultdict(list)
    for service in ServiceType.objects.all():
        services_by_category[service.category].append(service)

    return render(request, 'request_form.html', {'form': form, 'edit_mode': True, 'services_by_category': dict(services_by_category)})


# Request Delete View
@login_required
def request_delete_view(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk, car__owner=request.user)

    if req.status != 'Pending' or req.is_approved:
        messages.warning(request, "You can't delete this request. It’s already being processed.")
        return redirect('request-list')

    if request.method == 'POST':
        req.delete()
        messages.success(request, "Request deleted successfully.")
        return redirect('request-list')

    return render(request, 'request_confirm_delete.html', {'request_obj': req})


# Car List View
class CarListView(ListView):
    model = Car
    template_name = 'car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        return Car.objects.filter(owner=self.request.user)


# Car Create View
class CarCreateView(CreateView):
    model = Car
    fields = ['make', 'model', 'year', 'vin', 'horsepower', 'image']
    template_name = 'car_form.html'
    success_url = reverse_lazy('car-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Maintenance Request Create View
class MaintenanceRequestCreateView(CreateView):
    model = MaintenanceRequest
    form_class = MaintenanceRequestForm
    template_name = 'request_form.html'
    success_url = reverse_lazy('request-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        car_id = self.request.GET.get('car')
        if car_id:
            kwargs.setdefault('initial', {})['car'] = car_id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services_by_category = defaultdict(list)
        for service in ServiceType.objects.all():
            services_by_category[service.category].append(service)
        context['services_by_category'] = dict(services_by_category)
        return context

    def form_valid(self, form):
        service_id = self.request.POST.get("service")
        if not service_id:
            form.add_error(None, "Please select a service.")
            return self.form_invalid(form)
        form.instance.service_id = service_id
        return super().form_valid(form)


# Maintenance Request List View
class MaintenanceRequestListView(ListView):
    model = MaintenanceRequest
    template_name = 'request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(car__owner=self.request.user).select_related('car', 'service')


# Dashboard View
class DashboardView(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cars = Car.objects.filter(owner=user)
        requests = MaintenanceRequest.objects.filter(car__owner=user)

        context['total_cars'] = cars.count()
        context['total_requests'] = requests.count()
        context['completed_requests'] = requests.filter(status="Completed").count()
        context['upcoming_maintenance'] = requests.filter(requested_date__gte=timezone.now().date(), status="Pending").order_by("requested_date")[:3]

        return context


# Add Review View
@login_required
def add_review_view(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk, car__owner=request.user)

    if req.status != 'Completed':
        messages.warning(request, "You can only review completed services.")
        return redirect('request-list')

    if Review.objects.filter(request=req).exists():
        messages.info(request, "You’ve already submitted a review for this request.")
        return redirect('request-list')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.request = req
            review.save()
            messages.success(request, "Thanks for your feedback!")
            return redirect('request-list')
    else:
        form = ReviewForm()

    return render(request, 'review_form.html', {'form': form, 'req': req})


# Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile.html', {'form': form})


# Profile Edit View
@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)

        if form.has_changed() and form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        elif not form.has_changed():
            messages.warning(request, 'No changes were made to the profile.')

    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'profile_edit.html', {'form': form})
