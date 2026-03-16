# -*- coding: utf-8 -*-
"""
Views for PDF Course Sharing Platform
Developed by Marino ATOHOUN
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_exempt
import os

from .models import Course, PDFDocument, UserProfile, Newsletter, Advertisement, AdInteraction
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    CourseSerializer, PDFDocumentSerializer, PDFDocumentListSerializer,
    NewsletterSerializer, AdvertisementSerializer, AdInteractionSerializer
)
from .utils import decrypt_id


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class CourseListCreateView(generics.ListCreateAPIView):
    """View for listing and creating courses"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for course details"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PDFDocumentListCreateView(generics.ListCreateAPIView):
    """View for listing and creating PDF documents"""
    serializer_class = PDFDocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        queryset = PDFDocument.objects.filter(is_active=True)
        
        # Filter by course
        course_id = self.request.query_params.get('course', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by domain
        domain = self.request.query_params.get('domain', None)
        if domain:
            queryset = queryset.filter(course__domain__icontains=domain)
        
        # Search in title and description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PDFDocumentListSerializer
        return PDFDocumentSerializer


class PDFDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for PDF document details"""
    queryset = PDFDocument.objects.filter(is_active=True)
    serializer_class = PDFDocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        pk = self.kwargs.get('pk')
        # Try to decrypt if it's not a digit
        if not str(pk).isdigit():
            decoded_id = decrypt_id(pk)
            if decoded_id:
                pk = decoded_id
        
        return get_object_or_404(PDFDocument, id=pk, is_active=True)

    def get_permissions(self):
        """Only the uploader can update/delete their documents"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_update(self, serializer):
        # Only allow the uploader to update their document
        if serializer.instance.uploaded_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez modifier que vos propres documents.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow the uploader to delete their document
        if instance.uploaded_by != self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez supprimer que vos propres documents.")
        instance.is_active = False
        instance.save()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_pdf(request, document_id):
    """Download PDF file"""
    try:
        # Decrypt ID if it's not a digit
        if not str(document_id).isdigit():
            decoded_id = decrypt_id(document_id)
            if decoded_id:
                document_id = decoded_id
                
        document = get_object_or_404(PDFDocument, id=document_id, is_active=True)
        
        # Increment download count
        document.increment_download_count()
        
        # Serve the file
        if os.path.exists(document.pdf_file.path):
            with open(document.pdf_file.path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{document.title}.pdf"'
                return response
        else:
            raise Http404("Fichier non trouvé")
    except PDFDocument.DoesNotExist:
        raise Http404("Document non trouvé")


@api_view(['GET', 'HEAD'])
@permission_classes([permissions.AllowAny])
@xframe_options_exempt
def preview_pdf(request, document_id):
    """Preview PDF file in browser"""
    try:
        # Decrypt ID if it's not a digit
        if not str(document_id).isdigit():
            decoded_id = decrypt_id(document_id)
            if decoded_id:
                document_id = decoded_id
                
        document = get_object_or_404(PDFDocument, id=document_id, is_active=True)
        
        # Serve the file for preview
        if os.path.exists(document.pdf_file.path):
            response = FileResponse(open(document.pdf_file.path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{document.title}.pdf"'
            return response
        else:
            raise Http404("Fichier non trouvé")
    except PDFDocument.DoesNotExist:
        raise Http404("Document non trouvé")


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_documents(request):
    """Get documents uploaded by the current user"""
    documents = PDFDocument.objects.filter(
        uploaded_by=request.user,
        is_active=True
    ).order_by('-created_at')
    
    serializer = PDFDocumentListSerializer(documents, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def stats(request):
    """Get platform statistics"""
    total_documents = PDFDocument.objects.filter(is_active=True).count()
    total_courses = Course.objects.count()
    total_users = User.objects.count()
    total_downloads = sum(doc.download_count for doc in PDFDocument.objects.filter(is_active=True))
    
    return Response({
        'total_documents': total_documents,
        'total_courses': total_courses,
        'total_users': total_users,
        'total_downloads': total_downloads
    })


class NewsletterCreateView(generics.CreateAPIView):
    """View for newsletter subscription"""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.AllowAny]


class AdvertisementListView(generics.ListAPIView):
    """View for listing active advertisements"""
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from django.utils import timezone
        now = timezone.now()
        queryset = Advertisement.objects.filter(is_active=True)
        
        # Filter by date if set
        queryset = queryset.filter(
            (Q(start_date__isnull=True) | Q(start_date__lte=now)) &
            (Q(end_date__isnull=True) | Q(end_date__gte=now))
        )
        
        return queryset.order_by('?')

class AdInteractionCreateView(generics.CreateAPIView):
    """View for recording ad interactions"""
    serializer_class = AdInteractionSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Record IP and User Agent
        ip_address = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        user = self.request.user if self.request.user.is_authenticated else None
        
        serializer.save(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )

