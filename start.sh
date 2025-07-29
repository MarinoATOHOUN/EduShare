#!/bin/bash

# Script de démarrage pour EduShare
# Développé par Marino ATOHOUN

echo "🚀 Démarrage d'EduShare - Plateforme de Partage de Cours PDF"
echo "Développé par Marino ATOHOUN"
echo ""

# Vérification des dépendances
echo "📋 Vérification des dépendances..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

echo "✅ Dépendances vérifiées"
echo ""

# Démarrage du backend Django
echo "🔧 Démarrage du backend Django..."
cd "$(dirname "$0")"

# Vérifier si la base de données existe
if [ ! -f "db.sqlite3" ]; then
    echo "📊 Initialisation de la base de données..."
    python3 manage.py makemigrations
    python3 manage.py migrate
    
    echo "👤 Création du superutilisateur admin..."
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python3 manage.py shell
    
    echo "📚 Ajout des données de test..."
    python3 populate_data.py
fi

# Démarrer le serveur Django en arrière-plan
echo "🌐 Démarrage du serveur Django sur le port 8000..."
python3 manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Attendre que Django démarre
sleep 3

# Démarrage du frontend React
echo "⚛️ Démarrage du frontend React..."
cd frontend

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances frontend..."
    npm install
fi

# Démarrer le serveur React
echo "🌐 Démarrage du serveur React sur le port 5173..."
npm run dev -- --host 0.0.0.0 &
REACT_PID=$!

echo ""
echo "🎉 EduShare est maintenant en cours d'exécution !"
echo ""
echo "📍 URLs d'accès :"
echo "   Frontend (React) : http://localhost:5173"
echo "   Backend (Django) : http://localhost:8000"
echo "   Admin Django     : http://localhost:8000/admin"
echo ""
echo "👤 Comptes de test :"
echo "   Admin : admin / admin123"
echo "   User  : marie_dupont / password123"
echo ""
echo "⏹️ Pour arrêter les serveurs, appuyez sur Ctrl+C"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt des serveurs..."
    kill $DJANGO_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    echo "✅ Serveurs arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Attendre indéfiniment
wait

