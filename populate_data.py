#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to populate database with sample data
Developed by Marino ATOHOUN
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, UserProfile

def create_sample_data():
    """Create sample courses and users"""
    
    # Create sample courses
    courses_data = [
        {
            'name': 'Mathématiques',
            'domain': 'mathematiques',
            'description': 'Cours de mathématiques pour tous niveaux'
        },
        {
            'name': 'Informatique',
            'domain': 'informatique',
            'description': 'Cours de programmation et informatique'
        },
        {
            'name': 'Physique',
            'domain': 'physique',
            'description': 'Cours de physique générale et appliquée'
        },
        {
            'name': 'Chimie',
            'domain': 'chimie',
            'description': 'Cours de chimie organique et inorganique'
        },
        {
            'name': 'Biologie',
            'domain': 'biologie',
            'description': 'Cours de biologie cellulaire et moléculaire'
        },
        {
            'name': 'Histoire',
            'domain': 'histoire',
            'description': 'Cours d\'histoire contemporaine et ancienne'
        },
        {
            'name': 'Géographie',
            'domain': 'geographie',
            'description': 'Cours de géographie physique et humaine'
        },
        {
            'name': 'Littérature',
            'domain': 'litterature',
            'description': 'Cours de littérature française et mondiale'
        }
    ]
    
    print("Création des cours...")
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            domain=course_data['domain'],
            defaults={
                'name': course_data['name'],
                'description': course_data['description']
            }
        )
        if created:
            print(f"✓ Cours créé: {course.name}")
        else:
            print(f"- Cours existant: {course.name}")
    
    # Create sample users
    users_data = [
        {
            'username': 'marie_dupont',
            'email': 'marie.dupont@example.com',
            'first_name': 'Marie',
            'last_name': 'Dupont',
            'institution': 'Université de Paris'
        },
        {
            'username': 'jean_martin',
            'email': 'jean.martin@example.com',
            'first_name': 'Jean',
            'last_name': 'Martin',
            'institution': 'École Polytechnique'
        },
        {
            'username': 'sophie_bernard',
            'email': 'sophie.bernard@example.com',
            'first_name': 'Sophie',
            'last_name': 'Bernard',
            'institution': 'Sorbonne Université'
        }
    ]
    
    print("\nCréation des utilisateurs...")
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create user profile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'institution': user_data['institution']}
            )
            print(f"✓ Utilisateur créé: {user.username}")
        else:
            print(f"- Utilisateur existant: {user.username}")
    
    print("\n✅ Données de test créées avec succès!")
    print("\nComptes utilisateurs créés:")
    print("- admin / admin123 (superutilisateur)")
    for user_data in users_data:
        print(f"- {user_data['username']} / password123")

if __name__ == '__main__':
    create_sample_data()

