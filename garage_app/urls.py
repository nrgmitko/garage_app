from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CarListView, CarCreateView, MaintenanceRequestListView, MaintenanceRequestCreateView, DashboardView, \
    profile_view, profile_edit_view

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),

    # Car URLs
    path('cars/', CarListView.as_view(), name='car-list'),
    path('cars/add/', CarCreateView.as_view(), name='car-add'),
    path('cars/<int:pk>/edit/', views.car_edit_view, name='car-edit'),
    path('cars/<int:pk>/delete/', views.car_delete_view, name='car-delete'),

    # Maintenance Request URLs
    path('requests/', MaintenanceRequestListView.as_view(), name='request-list'),
    path('requests/add/', MaintenanceRequestCreateView.as_view(), name='request-add'),
    path('requests/<int:pk>/edit/', views.request_edit_view, name='request-edit'),
    path('requests/<int:pk>/delete/', views.request_delete_view, name='request-delete'),
    path('requests/<int:pk>/review/', views.add_review_view, name='request-review'),

    # Admin and Staff URLs
    path('admin/requests/', views.manage_requests_view, name='manage-requests'),
    path('staff/dashboard/', views.staff_dashboard_view, name='staff-dashboard'),

    # Profile and Password Change URLs
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile-edit'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='password_change.html',
        success_url='/profile/'
    ), name='password_change'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
