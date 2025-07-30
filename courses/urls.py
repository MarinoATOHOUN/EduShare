# -*- coding: utf-8 -*-
"""
URLs for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'courses'

urlpatterns = [
    # Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('my-documents/', views.user_documents, name='user_documents'),
    
    # Courses
    path('courses/', views.CourseListCreateView.as_view(), name='course_list_create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # PDF Documents
    path('documents/', views.PDFDocumentListCreateView.as_view(), name='document_list_create'),
    path('documents/<int:pk>/', views.PDFDocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:document_id>/download/', views.download_pdf, name='download_pdf'),
    path('documents/<int:document_id>/preview/', views.preview_pdf, name='preview_pdf'),
    
    # Statistics
    path('stats/', views.stats, name='stats'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)