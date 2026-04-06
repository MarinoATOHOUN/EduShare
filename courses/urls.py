# -*- coding: utf-8 -*-
"""
URLs for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .email_auth import EmailTokenObtainPairView
from . import views
from . import api_views
from .chat_views import DocumentChatView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'courses'

urlpatterns = [
    # Authentication
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
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
    path('documents/<str:pk>/', views.PDFDocumentDetailView.as_view(), name='document_detail'),
    path('documents/<str:document_id>/download/', views.download_pdf, name='download_pdf'),
    path('documents/<str:document_id>/preview/', views.preview_pdf, name='preview_pdf'),
    path('documents/<str:document_id>/chat/', DocumentChatView.as_view(), name='document_chat'),
    
    # Statistics
    path('stats/', views.stats, name='stats'),
    
    # Newsletter
    path('newsletter/', views.NewsletterCreateView.as_view(), name='newsletter_subscribe'),
    
    # Advertisements
    path('ads/', views.AdvertisementListView.as_view(), name='advertisement_list'),
    path('ads/interaction/', views.AdInteractionCreateView.as_view(), name='ad_interaction_create'),

    # Reference data
    path('study-levels/', views.StudyLevelListView.as_view(), name='study_level_list'),

    # Developer / API access
    path('developer/plans/', api_views.APIPlanListView.as_view(), name='api_plan_list'),
    path('developer/subscription/', api_views.CurrentSubscriptionView.as_view(), name='api_current_subscription'),
    path('developer/api-keys/', api_views.APIKeyListCreateView.as_view(), name='api_key_list_create'),
    path('developer/api-keys/<int:key_id>/revoke/', api_views.APIKeyRevokeView.as_view(), name='api_key_revoke'),

    # Data API (API key auth)
    path('data/documents/', api_views.DataDocumentListView.as_view(), name='data_document_list'),
    path('data/documents/<str:document_id>/download/', api_views.DataDocumentDownloadView.as_view(), name='data_document_download'),
    path('data/whoami/', api_views.DataWhoAmIView.as_view(), name='data_whoami'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
